from flask import Flask, request, jsonify
import re
import nltk
from nltk.tag import CRFTagger
import os
from nltk.parse.chart import SteppingChartParser, FilteredSingleEdgeFundamentalRule
from nltk.parse.chart import LeafInitRule, FilteredBottomUpPredictCombineRule
from anyascii import anyascii
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

nltk.download("punkt")
nltk.download("tagsets")

app = Flask(__name__)


def preprocess_news_content(news_str):
    """Membagi paragraf - paragraf berita dengan separator '\n\n' lalu
    membagi string berita tersebut lagi per kalimat dan melakukan text
    preprocessing.
    """
    # Ekstraksi konten dari HTML Rich Text dengan BeautifulSoup4
    soup = BeautifulSoup(news_str, "html.parser")
    news_html_free = soup.get_text()

    # Ubah semua karakter unicode menjadi ASCII yang paling mendekati
    news_html_free = anyascii(news_html_free)

    # Ubah karakter menjadi lowercase.
    news_html_free = news_html_free.lower()

    # Bagi string berdasarkan separator dua newline ('\n\n').
    paragraphs_list = news_html_free.split("\n\n")
    tokenized_sentences_list = []

    for paragraph in paragraphs_list:
        # Ubah karakter - karakter whitespace ('\t', '\n', '\r', ' ')
        # menjadi satu space (' ').
        paragraph = re.sub(r"\s+", r" ", paragraph)

        # Buang leading & trailing whitespace
        paragraph = paragraph.strip()

        # Ubah double single quote ('') menjadi double quote (").
        paragraph = re.sub(r"''", r'"', paragraph)

        # Pisahkan tanda titik terakhir dari bilangan agar tanda titik dapat
        # dipisahkan oleh nltk.tokenize.word_tokenize().
        # CONTOH KODE:
        # print(re.sub(r'\b(?P<myNum>[0-9]+)\.\B', r'\g<myNum> .',
        #       '2023.2112,232,1313. 20323.3234,234,1313, 20323.3234,234,1313.')
        # )
        # print(re.findall(r'\b[0-9]+\.\B',
        #       'pada tahun 2022. pada tahun 2023. 11.22.33. 2024 2025.2026.3122.')
        # )
        #
        # OUTPUT:
        # 2023.2112,232,1313 . 20323.3234,234,1313, 20323.3234,234,1313 .
        # ['2022.', '2023.', '33.', '3122.']
        paragraph = re.sub(r"\b(?P<myNum>[0-9]+)\.\B", r"\g<myNum> .", paragraph)

        # Skip paragraph bila paragraph berisi pesan otomatis dari Google
        # NOTE: Hapus kodeini saat fungsi ini digunakan untuk preprocessing
        # pada aplikasi final.
        # google_pattern = r'you received this message because you are subscribed to the'
        # if re.search(google_pattern, paragraph):
        #     continue

        # Skip paragraf bila paragraf berisi link website (untuk mempermudah
        # training).
        # NOTE: Hapus kode ini saat fungsi ini digunakan untuk preprocessing
        # pada aplikasi final.
        # http_pattern = r'http'
        # if re.search(http_pattern, paragraph):
        #     continue

        # Skip paragraf bila konten mengandung karakter UTF-8 (untuk mempermudah
        # training)
        # NOTE: Hapus kode ini saat fungsi ini digunakan untuk preprocessing
        # pada aplikasi final.
        # utf_8_pattern = r'='
        # if re.search(utf_8_pattern, paragraph):
        #     continue

        # Melakukan tokenization.
        tokenized_paragraph = nltk.tokenize.word_tokenize(paragraph)

        # Loop untuk mengelompokkan token-token tersebut per kalimat.
        is_in_quotation = False
        is_terminal_found_inside_quotation = False
        last_symbol_found_inside_quotation = ""
        num_of_quote_inside_quote = 0
        temp_tokenized_sentence = []
        for token in tokenized_paragraph:
            """NOTE:
            Kalimat di dalam tanda kutip termasuk kalimat lisan
            (kalimat yang diucapkan tanpa batasan grammar) sehingga
            tidak bisa dideteksi apakah sintaksnya benar atau tidak.
            Oleh karena itu, semua kata-kata dalam tanda kutip (kecuali
            tanda koma, titik, tanya, dan seru) akan di-skip.
            """

            """NOTE: 
            Kutipan di dalam suatu kutipan juga akan diabaikan
            """

            """NOTE:
            Dua backtick (``)       = Kutip dua awal (start quotation).
            Dua kutip tunggal ('')  = Kutip dua akhir (end quotation).
            """

            # Bila ditemukan tanda kutip dua awal dan sekarang ini belum berada
            # di dalam kutipan, ubah status menjadi di dalam kutipan (tanda
            # kutip awal ini disimpan).
            if token == "``" and not is_in_quotation:
                temp_tokenized_sentence.append(token)
                is_in_quotation = True

            # Bila ditemukan tanda kutip dua awal dan sekarang ini sedang
            # berada di dalam kutipan, tambahkan nilai
            # "num_of_quote_inside_quote" (tanda kutip awal ini tidak disimpan).
            elif token == "``" and is_in_quotation:
                num_of_quote_inside_quote += 1

            # Bila ditemukan tanda kutip dua akhir dan tidak ditemukan tanda
            # kutip dua awal lain yang belum berpasangan, simpan simbol terakhir
            # yang ditemukan di dalam kutipan dan simpan tanda kutip akhir
            # tersebut.
            if token == "''" and num_of_quote_inside_quote == 0:
                if len(last_symbol_found_inside_quotation) > 0:
                    temp_tokenized_sentence.append(last_symbol_found_inside_quotation)
                temp_tokenized_sentence.append(token)
                is_in_quotation = False
                last_symbol_found_inside_quotation = ""

            # Bila ditemukan tanda kutip dua akhir dan ditemukan tanda kutip
            # dua awal lainnya yang belum berpasangan, kurangi nilai
            # "num_of_quote_inside_quote" (tanda kutip akhir ini tidak
            # disimpan).
            elif token == "''" and num_of_quote_inside_quote > 0:
                num_of_quote_inside_quote -= 1

            # Simpan semua kata dan simbol di luar kutipan akan dimasukkan
            if not is_in_quotation and token != "''":
                temp_tokenized_sentence.append(token)

            # Bila ditemukan simbol terminal atau tanda koma di dalam
            # kutipan, simpan simbol tersebut dalam variabel sementara.
            if is_in_quotation and re.search(r"^[.?!,]$", token):
                last_symbol_found_inside_quotation = token

            # Bila ditemukan tanda terminal (.!?) kalimat dan sekarang ini tidak
            # sedang berada di dalam kuotasi, kelompokkan token-token ini
            # menjadi satu kalimat.
            if not is_in_quotation and re.search(r"^[.?!]$", token):
                tokenized_sentences_list.append(temp_tokenized_sentence)
                temp_tokenized_sentence = []
                last_symbol_found_inside_quotation = ""

            # Bila ditemukan tanda terminal (.!?) kalimat dan sekarang ini
            # di dalam kuotasi, pisahkan kalimat bila karakter setelahnya
            # adalah tanda kutip dua akhir.

            # Bila ditemukan tanda terminal di dalam kuotasi dan tidak ada
            # tanda kutip lainnya di dalam kuotasi yang belum berpasangan.
            if (
                is_in_quotation
                and re.search(r"^[.?!]$", token)
                and num_of_quote_inside_quote == 0
            ):
                is_terminal_found_inside_quotation = True
            else:
                # Bila tanda sekarang ini adalah tanda kutip akhir dan ditemukan
                # tanda terminal di dalam kuotasi, kelompokkan token-token ini
                # menjadi satu kalimat.
                if (
                    token == "''"
                    and is_terminal_found_inside_quotation == True
                    and num_of_quote_inside_quote == 0
                ):
                    tokenized_sentences_list.append(temp_tokenized_sentence)
                    temp_tokenized_sentence = []
                    is_terminal_found_inside_quotation = False
                # Selain semua hal di atas, ubah
                # is_terminal_found_inside_quotation menjadi false karena
                # tanda terminal itu (bila ada) tidak lagi bersebelahan dengan
                # tanda kutip akhir.
                else:
                    is_terminal_found_inside_quotation = False

                    # Jika token saat ini bukan tanda terminal atau tanda koma,
                    # set last_symbol_found_inside_quotation menjadi ''.
                    if not re.search(r"^[.?!,]$", token):
                        last_symbol_found_inside_quotation = ""

        # Simpan sisa token di dalam temp list sebagai "kalimat tanpa
        # tanda terminal."
        if len(temp_tokenized_sentence) != 0:
            tokenized_sentences_list.append(temp_tokenized_sentence)
            temp_tokenized_sentence = []

    return tokenized_sentences_list


# Siapkan CRF dan CFG
def initialize_crf_cfg():
    """NOTE:
    - os.getcwd()   --> Print working directory (not suitable for modules).
    - __file__      --> Print absolute path for this file "main.py" (suitable
                        for modules).
    """
    # print("os.getcwd(): " + os.getcwd())
    # print("__file__: " + __file__)
    model_path = os.path.dirname(os.path.abspath(__file__))
    print("model_path: ", model_path)
    grammar = nltk.data.load(
        "file:" + os.path.join(model_path, "utapis_sintaksis_kalimat_v2.cfg"), "cfg"
    )

    LEFT_CORNER_STRATEGY = [
        LeafInitRule(),
        FilteredBottomUpPredictCombineRule(),
        FilteredSingleEdgeFundamentalRule(),
    ]

    utapis_scp = SteppingChartParser(
        grammar=grammar, strategy=LEFT_CORNER_STRATEGY, trace=0
    )

    utapis_crf_tagger = CRFTagger()
    utapis_crf_tagger.set_model_file(
        os.path.join(model_path, "utapis_crf_model.crf.tagger")
    )

    return utapis_crf_tagger, utapis_scp


def get_tagged_sentences(crf_tagger, preprocessed_sentence_list):
    return crf_tagger.tag_sents(preprocessed_sentence_list)


# Melakukan parsing dengan SteppingChartParser Left-Corner Strategy dengan
# Early Stopping (berhenti bila ditemukan hasil).
def stepping_chart_parsing(scp, tags):
    scp.initialize(tags)

    for step in scp.step():
        # Berhenti bila ditemukan parsing yang lengkap.
        if len(list(scp.parses())) > 0:
            break

        # Berhenti bila sudah tidak ada lagi kemungkinan parsing
        # yang bisa ditambahkan.
        if step is None:
            break

    # Return generator.
    return scp.parses()


# Mengembalikan list boolean yang menyatakan bahwa sintaksis suatu kalimat
# benar atau tidak (menggunakan SteppingChartParser).
def get_cfg_bool_results(scp, list_of_tags):
    num_of_sentences = len(list_of_tags)
    print(f"Found {num_of_sentences} sentences!")

    tag_only_sentences = []
    for tagged_sent in list_of_tags:
        tag_only_sentences.append([x[1] for x in tagged_sent])

    cfg_results = []
    for idx, (tags, tags_and_words) in enumerate(zip(tag_only_sentences, list_of_tags)):
        generator = stepping_chart_parsing(scp, tags)
        generator_content_count = len(list(generator))

        if generator_content_count <= 0:
            cfg_results.append(False)
            print(f"Sentence {idx + 1}/{num_of_sentences} = {tags_and_words}: {False}!")
        elif generator_content_count > 0:
            cfg_results.append(True)
            print(f"Sentence {idx + 1}/{num_of_sentences} = {tags_and_words}: {True}!")

    return cfg_results


# Handler untuk pengecekan sintaksis kalimat.
@app.route("/utapis-cek-sintaksis-kal", methods=["POST"])
def utapis_cek_sintaksis_kal_handler():
    now = datetime.now(tz=pytz.timezone("Asia/Jakarta"))
    print(
        f"New request received from {request.remote_addr} at {now.strftime('%Y-%b-%d %H:%M:%S')}"
    )

    false_only = request.args.get("false-only", False)
    false_only = True if false_only == "1" else False
    bool_only = request.args.get("bool-only", False)
    bool_only = True if bool_only == "1" else False

    if false_only:
        print("Additional Request Option: False Only")
    elif bool_only:
        print("Additional Request Option: Bool Only")

    article = request.form.get("article", "")
    if len(article.strip()) <= 0:
        print(
            f"Request from {request.remote_addr} finished at {now.strftime('%Y-%b-%d %H:%M:%S')} (Status: 400)!"
        )
        return jsonify({"error": "Empty article input"}), 400

    preprocessed_article = preprocess_news_content(article)
    tagged_sentences = get_tagged_sentences(utapis_crf_tagger, preprocessed_article)

    results = get_cfg_bool_results(utapis_scp, tagged_sentences)

    now = datetime.now(tz=pytz.timezone("Asia/Jakarta"))
    print(
        f"Request from {request.remote_addr} finished at {now.strftime('%Y-%b-%d %H:%M:%S')} (Status: 200)!"
    )
    print()

    # Hanya return kalimat-kalimat yang gagal diparsing.
    if false_only == True:
        filtered_tagged_sentences = []
        for result, tagged_sentence in zip(results, tagged_sentences):
            if result == False:
                filtered_tagged_sentences.append(tagged_sentence)
        return jsonify({"tagged_sentences": filtered_tagged_sentences}), 200

    # Hanya return hasil parsing (tanpa hasil labeling/tagging).
    if bool_only == True:
        return jsonify({"results": results}), 200

    return jsonify({"tagged_sentences": tagged_sentences, "results": results}), 200


# Handler bila url yang digunakan salah.
@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"error": "Page not found"}), 404


# Initialize CRF & CFG to global.
utapis_crf_tagger, utapis_scp = initialize_crf_cfg()

if __name__ == "__main__":
    app.run(debug=True, host="localhost", port=8000)
    # app.run(debug=False, host="0.0.0.0", port=5000)

# Run Flask from Command Line (Development Mode).
# NOTE: (if __name__ = "__main__") will not be run.
# flask --app utapis_flask_server\main.py run --host localhost --port 8000

# NOTE:
# - Use python -m build to create the module's distribution ('tar.gz' and '.whl' file in
# 'dist' directory).
# - Then, install the wheel file using pip install.

# Run waitress from Command Line (Production Mode).
# pip install dist\utapis_flask_server-1.0.0-py3-none-any.whl
# waitress-serve --host=127.0.0.1 --port=8000 utapis_sintaksis_flask_server.main:app
# waitress-serve --host=localhost --port=8080 utapis_sintaksis_flask_server.main:app
# waitress-serve --listen=*:8080 utapis_sintaksis_flask_server.main:app
# waitress-serve --host=10.100.1.99 --port=8080 utapis_sintaksis_flask_server.main:app

# cURL Testing Code:
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" http://localhost:8000/utapis-cek-sintaksis-kal -d "article=Dia pergi ke pasar."
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" http://127.0.0.1:8000/utapis-cek-sintaksis-kal -d "article=Dia pergi ke pasar."
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" http://10.100.1.99:8080/utapis-cek-sintaksis-kal -d "article=Dia pergi ke pasar."
