'''Service 2'''
@app.route('/inventory/add', methods=['POST'])
def add_goods():
    data = request.get_json()
    name = data.get('name')
    category = data.get('category')
    price = data.get('price')
    description = data.get('description')
    count = data.get('count')

    if not (name and category and price and count is not None):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO inventory (name, category, price, description, count)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (name, category, price, description, count)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return jsonify({"message": "Item added successfully"}), 201

@app.route('/inventory/<int:item_id>/deduct', methods=['PUT'])
def deduct_goods(item_id):
    data = request.get_json()
    count = data.get('count')

    if not count or count <= 0:
        return jsonify({"error": "Invalid count"}), 400

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute("SELECT count FROM inventory WHERE id = %s", (item_id,))
        item = cur.fetchone()

        if not item:
            return jsonify({"error": "Item not found"}), 404

        if item[0] < count:
            return jsonify({"error": "Insufficient stock"}), 400

        cur.execute(
            "UPDATE inventory SET count = count - %s WHERE id = %s",
            (count, item_id)
        )
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return jsonify({"message": "Stock deducted successfully"}), 200

@app.route('/inventory/<int:item_id>/update', methods=['PATCH'])
def update_goods(item_id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    updates = []
    values = []
    for key, value in data.items():
        updates.append(sql.Identifier(key) + sql.SQL(" = %s"))
        values.append(value)

    conn = get_db_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            sql.SQL("UPDATE inventory SET ") +
            sql.SQL(", ").join(updates) +
            sql.SQL(" WHERE id = %s"),
            values + [item_id]
        )
        if cur.rowcount == 0:
            return jsonify({"error": "Item not found"}), 404
        conn.commit()
    finally:
        cur.close()
        conn.close()

    return jsonify({"message": "Item updated successfully"}), 200
