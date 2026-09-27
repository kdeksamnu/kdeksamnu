@app.route("/recipes/<int:recipe_id>", methods=["PUT"])
@token_required
def update_recipe_put(current_user, recipe_id):
  data = request.get_json()
  if not data or not data.get("title") or not data.get("ingredients") or not data.get("instructions"):
    return jsonify({"error": "Missing required fields"}), 400

  db = get_db()
  cursor = db.cursor()

  # 1) Load the recipe by ID only to check existence
  cursor.execute(
      "SELECT id, user_id FROM recipes WHERE id = ?",
      (recipe_id,),
  )
  recipe = cursor.fetchone()

  if not recipe:
    return jsonify({"error": "Recipe not found"}), 404

  # 2) Authorization: owner OR admin
  is_owner = (recipe["user_id"] == current_user["id"])
  is_admin = (current_user.get("role") == "admin")

  if not (is_owner or is_admin):
    return jsonify({"error": "Forbidden"}), 403

  # 3) Execute the update
  cursor.execute(
      "UPDATE recipes SET title = ?, ingredients = ?, instructions = ? WHERE id = ?",
      (data["title"], data["ingredients"], data["instructions"], recipe_id),
  )
  db.commit()

  return jsonify({"message": "Recipe updated successfully"}), 200


@app.route("/recipes/<int:recipe_id>", methods=["DELETE"])
@token_required
def delete_recipe(current_user, recipe_id):
    db = get_db()
    cursor = db.cursor()

    # 1) Load the recipe by ID only to check existence
    cursor.execute(
        "SELECT id, user_id FROM recipes WHERE id = ?",
        (recipe_id,),
    )
    recipe = cursor.fetchone()

    if not recipe:
        return jsonify({"error": "Recipe not found"}), 404

    # 2) Authorization: owner OR admin
    is_owner = (recipe["user_id"] == current_user["id"])
    is_admin = (current_user.get("role") == "admin")

    if not (is_owner or is_admin):
        return jsonify({"error": "Forbidden"}), 403

    # 3) Execute the deletion
    cursor.execute("DELETE FROM recipes WHERE id = ?", (recipe_id,))
    db.commit()

    return "", 204
