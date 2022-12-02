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
