from app import app

if __name__ == '__main__':
    app.run(debug=True)
    for rule in app.url_map.iter_rules():
        print(rule)