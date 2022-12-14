from bs4 import BeautifulSoup
from anyascii import anyascii

html_entities_doc = """<p>kalimat pertama</p>
<p>kalimat kedua &lt &amp &#342;</p>
<p>kalimat&nbsp;ketiga & ketiga juga</p>
<p>kalimat &nbsp; keempat</p>
<p>kalimat <b>kel<i>i</i>ma</b></p>
<p>kalimat keenam</a>
"""

soup_html_parser = BeautifulSoup(html_entities_doc, "html.parser")
# print(" ".join(soup_html_parser.strings))
print(" ".join(soup_html_parser.stripped_strings))
# print("anyascii:", anyascii(" ".join(soup_html_parser.stripped_strings)))
print()

# NOTE: repr() --> "Representation" of the string, rather than printing the string
#                  directly.
print(soup_html_parser.get_text())
print(repr(soup_html_parser.get_text()))
print(repr(anyascii(soup_html_parser.get_text())))
print()

unwrap_test_doc = """
<html>
<body>
<p>Ini a<b>da<i>l</i>a</b>h <span><b><span>ka<span>li<b><i>m</i></b>a</span>t</span></b></span>.</p>
</html>
"""

unwrap_test_parser = BeautifulSoup(unwrap_test_doc, "html.parser")
# print(type(unwrap_test_parser))
# print(unwrap_test_parser.p)
# print(type(unwrap_test_parser.p))

# unwrap_test_children = unwrap_test_parser.contents
# print(unwrap_test_children)
# print(type(unwrap_test_children[0]))

# unwrap_test_descendants = [d for d in unwrap_test_parser.descendants]
# print(unwrap_test_descendants)
# print(type(unwrap_test_descendants[0]))
# print(type(unwrap_test_descendants[2]))

result_get_text = unwrap_test_parser.get_text()
print(repr(result_get_text))

plain_text = "Hello&nbsp;World!"
plain_text_parser = BeautifulSoup(plain_text, "html.parser")
print(repr(plain_text_parser.get_text()))
print(repr(anyascii(plain_text_parser.get_text())))

raw_dari_website_utapis = """<p><strong>TRIBUNNEWS.COM</strong>&nbsp;-&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/lembaga-perlindungan-saksi-dan-korban">Lembaga Perlindungan Saksi dan Korban</a>&nbsp;(LPSK) mengajukan rekomendasi permohonan keringanan hukuman terhadap&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/bharada-richard-eliezer">Bharada Richard Eliezer</a>&nbsp;atau Bharada E dalam kasus pembunuhan Brigadir Nofriansyah Yosua Hutabarat atau&nbsp;<a class="blue" href="https://www.tribunnews.com/tag/brigadir-j">Brigadir J</a>.</p>\r\n<p>Pasalnya, Bharada Eliezer bersedia menjadi Justice Collaborator (JC) dalam membuka kasus ini.</p>\r\n<p>Apalagi kasus ini menyangkut kebohongan seorang perwira polri yang seharusnya menjadi penegak hukum.</p>"""
parser = BeautifulSoup(raw_dari_website_utapis, "html.parser")
result = parser.get_text()
print(repr(result))
print(repr(anyascii(result)))
print(anyascii(result))
