from flask import Flask, request

app = Flask(__name__)

# Handler untuk pengecekan sintaksis kalimat.
@app.route('/utapis-cek-sintaksis-kal', methods=['POST'])
def utapis_cek_sintaksis_kal_handler():
    article = request.form.get('article', '')
    if len(article.strip()) <= 0:
        return {"error": "Empty article input"}, 400

    return {"article": article}, 200

# Handler bila url yang digunakan salah.
@app.errorhandler(404)
def page_not_found(e):
    return {"error": "Page not found"}, 404

if __name__ == '__main__':
    app.run(debug=True, host="localhost", port=5000)

# cURL Testing Code:
# curl -X POST -H "Content-Type: application/x-www-form-urlencoded" http://localhost:5000/utapis-cek-sintaksis-kal -d "article=Dia pergi ke pasar"

