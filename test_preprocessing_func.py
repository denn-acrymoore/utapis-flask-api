import re
import nltk
from anyascii import anyascii
from bs4 import BeautifulSoup

nltk.download("punkt")
nltk.download("tagsets")


def preprocess_news_content(news_str):
    """Membagi paragraf - paragraf berita dengan separator '\n' lalu
    membagi string berita tersebut lagi per kalimat dan melakukan text
    preprocessing.
    """

    # Unescape backslashes.
    # - Ubah \\n dan \\r menjadi \n.
    # - Ubah \\t \\f dan \\v menjadi " " (space).
    # Link: https://docs.python.org/3/howto/regex.html#the-backslash-plague
    # Link: https://www.toppr.com/guides/python-guide/references/methods-and-functions/methods/string/isspace/python-string-isspace/
    news_str = re.sub(r"(\\n|\\r)", r"\n", news_str)
    news_str = re.sub(r"(\\t|\\f|\\v)", r" ", news_str)

    # print("Article RAW Unescaped WhiteSpace:")
    # print(repr(news_str))

    # Ekstraksi konten dari HTML Rich Text dengan BeautifulSoup4
    soup = BeautifulSoup(news_str, "html.parser")
    news_html_free = soup.get_text()
    # print("BeautifulSoup:")
    # print(repr(news_html_free))

    # Ubah semua karakter unicode menjadi ASCII yang paling mendekati
    news_html_free = anyascii(news_html_free)
    # print("anyascii:")
    # print(repr(news_html_free))

    # Bagi string berdasarkan separator newline ('\n').
    # NOTE: Menggunakan separator \n, bukan \n\n karena
    #       beautiful soup akan mengubah \n+ menjadi \n.
    paragraphs_list = news_html_free.split("\n")
    # print("split():")
    # print(repr(paragraphs_list))
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


def preprocess_separate_sentences(news_str):
    """Membagi paragraf - paragraf berita dengan separator '\n' lalu
    membagi string berita tersebut lagi per kalimat (tanpa preprocessing untuk
    CRF dan CFG).
    """
    # Unescape backslashes.
    # - Ubah \\n dan \\r menjadi \n.
    # - Ubah \\t \\f dan \\v menjadi " " (space).
    # Link: https://docs.python.org/3/howto/regex.html#the-backslash-plague
    # Link: https://www.toppr.com/guides/python-guide/references/methods-and-functions/methods/string/isspace/python-string-isspace/
    news_str = re.sub(r"(\\n|\\r)", r"\n", news_str)
    news_str = re.sub(r"(\\t|\\f|\\v)", r" ", news_str)

    # Ekstraksi konten dari HTML Rich Text dengan BeautifulSoup4
    soup = BeautifulSoup(news_str, "html.parser")
    news_html_free = soup.get_text()

    # Ubah semua karakter unicode menjadi ASCII yang paling mendekati
    news_html_free = anyascii(news_html_free)

    # Bagi string berdasarkan separator newline ('\n').
    # NOTE: Menggunakan separator \n, bukan \n\n karena
    #       beautiful soup akan mengubah \n+ menjadi \n.
    paragraphs_list = news_html_free.split("\n")
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

        # Melakukan tokenization.
        tokenized_paragraph = nltk.tokenize.word_tokenize(paragraph)

        # Loop untuk mengelompokkan token-token tersebut per kalimat.
        is_in_quotation = False
        is_terminal_found_inside_quotation = False
        num_of_quote_inside_quote = 0
        temp_tokenized_sentence = []
        for token in tokenized_paragraph:
            """NOTE:
            Dua backtick (``)       = Kutip dua awal (start quotation).
            Dua kutip tunggal ('')  = Kutip dua akhir (end quotation).
            """

            # Masukkan semua token ke dalam temp_tokenized_sentence
            temp_tokenized_sentence.append(token)

            # Bila ditemukan tanda kutip dua awal dan sekarang ini belum berada
            # di dalam kutipan, ubah status menjadi di dalam kutipan (tanda
            # kutip awal ini disimpan).
            if token == "``" and not is_in_quotation:
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
                is_in_quotation = False

            # Bila ditemukan tanda kutip dua akhir dan ditemukan tanda kutip
            # dua awal lainnya yang belum berpasangan, kurangi nilai
            # "num_of_quote_inside_quote" (tanda kutip akhir ini tidak
            # disimpan).
            elif token == "''" and num_of_quote_inside_quote > 0:
                num_of_quote_inside_quote -= 1

            # Bila ditemukan tanda terminal (.!?) kalimat dan sekarang ini tidak
            # sedang berada di dalam kuotasi, kelompokkan token-token ini
            # menjadi satu kalimat.
            if not is_in_quotation and re.search(r"^[.?!]$", token):
                tokenized_sentences_list.append(temp_tokenized_sentence)
                temp_tokenized_sentence = []

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

        # Simpan sisa token di dalam temp list sebagai "kalimat tanpa
        # tanda terminal."
        if len(temp_tokenized_sentence) != 0:
            tokenized_sentences_list.append(temp_tokenized_sentence)
            temp_tokenized_sentence = []

    untokenized_sentences_list = []
    for token_sents in tokenized_sentences_list:
        # Gabungkan token-token menjadi satu string yang dibatasi satu spasi.
        temp_untokenized_sentence = " ".join(token_sents)

        # Buang spasi di sebelah kiri tanda baca ;,.?!
        temp_untokenized_sentence = re.sub(
            r"\s+(?P<punctuation>[;,.?!])",
            r"\g<punctuation>",
            temp_untokenized_sentence,
        )

        # Buang spasi di sebelah kanan tanda ``
        temp_untokenized_sentence = re.sub(r"``\s+", r"``", temp_untokenized_sentence)

        # Buang spasi di sebelah kiri tanda ''
        temp_untokenized_sentence = re.sub(r"\s+''", r"''", temp_untokenized_sentence)

        # Buang spasi di sebelah kanan tanda (<[{
        temp_untokenized_sentence = re.sub(
            r"(?P<punctuation>[\(\<\[\{])\s+",
            r"\g<punctuation>",
            temp_untokenized_sentence,
        )

        # Buang spasi di sebelah kiri tanda )>]}
        temp_untokenized_sentence = re.sub(
            r"\s+(?P<punctuation>[\)\>\]\}])",
            r"\g<punctuation>",
            temp_untokenized_sentence,
        )

        # Buang spasi di sebelah kiri dan kanan tanda -
        temp_untokenized_sentence = re.sub(r"\s*-\s*", r"-", temp_untokenized_sentence)

        # Buang spasi di sebelah kiri tanda '
        # NOTE: nltk.tokenize.word_tokenize("hello 'world lmao' hello.")
        # = ['hello', "'world", 'lmao', "'", 'hello', '.']
        temp_untokenized_sentence = re.sub(r"\s+'\B", r"'", temp_untokenized_sentence)

        # Buang spasi di antara angka dengan tanda %
        temp_untokenized_sentence = re.sub(
            r"(?P<num>\d+)\s+(?P<punctuation>%)",
            r"\g<num>\g<punctuation>",
            temp_untokenized_sentence,
        )

        # Buang spasi di antara kata dengan tanda @#$
        temp_untokenized_sentence = re.sub(
            r"(?P<punctuation>[@#$])\s+(?P<word>\w+)",
            r"\g<punctuation>\g<word>",
            temp_untokenized_sentence,
        )

        # Ubah `` dan '' menjadi "
        temp_untokenized_sentence = re.sub(r"``|''", r'"', temp_untokenized_sentence)

        untokenized_sentences_list.append(temp_untokenized_sentence)

    return untokenized_sentences_list


# test_raw_data = """<p><strong>TRIBUNNEWS.COM</strong>&nbsp;-&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/lembaga-perlindungan-saksi-dan-korban">Lembaga Perlindungan Saksi dan Korban</a>&nbsp;(LPSK) mengajukan rekomendasi permohonan keringanan hukuman terhadap&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/bharada-richard-eliezer">Bharada Richard Eliezer</a>&nbsp;atau Bharada E dalam kasus pembunuhan Brigadir Nofriansyah Yosua Hutabarat atau&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/brigadir-j">Brigadir J</a>.</p>\r\n<p>Pasalnya, Bharada Eliezer bersedia menjadi Justice Collaborator (JC) dalam membuka kasus ini.</p>\r\n<p>Apalagi kasus ini menyangkut kebohongan seorang perwira polri yang seharusnya menjadi penegak hukum.</p>"""
# print("Article RAW:")
# print(repr(test_raw_data))
# print()

# result = preprocess_news_content(test_raw_data)
# print(repr(result))
# print(f"length: {len(result)}")
# print()

# result = preprocess_separate_sentences(test_raw_data)
# print(repr(result))
# print(f"length: {len(result)}")
# print()


# test_raw_data = """
# Hello world!!!
# Hello (nope<lmao>)world-lmao[yeet].
# Hello 5% there.!@
# Menang 5:0\\n
# tagar #relatable hello.
# Hello @instagram_hello
# $500 harga murah.
# "Dia PERGI ke taman," ujar sultan syahrir.
# Seminar bertajuk 'harmonia', 'pelangi di ujung taman', dan 'kasih'.
# ''Fantasia''.
# """

test_raw_data = """<p><strong>TRIBUNNEWS.COM</strong>&nbsp;-&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/lembaga-perlindungan-saksi-dan-korban">Lembaga Perlindungan Saksi dan Korban</a>&nbsp;(LPSK) mengajukan rekomendasi permohonan keringanan hukuman terhadap&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/bharada-richard-eliezer">Bharada Richard Eliezer</a>&nbsp;atau Bharada E dalam kasus pembunuhan Brigadir Nofriansyah Yosua Hutabarat atau&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/brigadir-j">Brigadir J</a>.</p>\r\n<p>Pasalnya, Bharada Eliezer bersedia menjadi Justice Collaborator (JC) dalam membuka kasus ini.</p>\r\n<p>Apalagi kasus ini menyangkut kebohongan seorang perwira polri yang seharusnya menjadi penegak hukum.</p>"""

print("Article RAW:")
print(repr(test_raw_data))
print()

result = preprocess_news_content(test_raw_data)
print(repr(result))
print(f"length: {len(result)}")
print()

result = preprocess_separate_sentences(test_raw_data)
print(repr(result))
print(f"length: {len(result)}")
print()

result = preprocess_news_content("Dia <tono> pergi.")
print(repr(result))

result = preprocess_news_content(
    "1. Pencabutan aturan Omnibus Law UU Nomor 6 Tahun 2023 tentang Cipta Kerja."
)
print(repr(result))
