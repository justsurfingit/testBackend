from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
app = Flask(__name__)
CORS(app)
data_file_path = os.path.join(os.path.dirname(__file__), '../store/data.json')

with open(data_file_path) as f:
    properties = json.load(f)


FALLBACK_IMAGE = "https://images.unsplash.com/photo-1560518883-ce09059eeffa?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&q=60"

@app.route('/api/properties', methods=['GET'])
def get_properties():
    for property in properties:
        if not property.get('image_url') or 'random' in property.get('image_url', ''):
            property['image_url'] = FALLBACK_IMAGE
    return jsonify(properties)

@app.route('/api/properties/<int:id>', methods=['GET'])
def get_property(id):
    property = next((p for p in properties if p['id'] == id), None)
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    
    # Ensure property has valid image URL
    if not property.get('image_url') or 'random' in property.get('image_url', ''):
        property['image_url'] = FALLBACK_IMAGE
    
    return jsonify(property)

@app.route('/api/properties', methods=['POST'])
def create_property():
    new_property = request.json
    if not all(key in new_property for key in ('name', 'price', 'location', 'bedrooms', 'bathrooms')):
        return jsonify({'error': 'Missing required fields'}), 400
    new_property['id'] = max(p['id'] for p in properties) + 1
    
    if not new_property.get('image_url'):
        new_property['image_url'] = FALLBACK_IMAGE
    
    properties.append(new_property)
    with open(data_file_path, 'w') as f:
        json.dump(properties, f)
    return jsonify(new_property), 201

@app.route('/api/properties/<int:id>', methods=['PUT'])
def update_property(id):
    property = next((p for p in properties if p['id'] == id), None)
    if not property:
        return jsonify({'error': 'Property not found'}), 404
    data = request.json
    property.update(data)
    
    if not property.get('image_url') or 'random' in property.get('image_url', ''):
        property['image_url'] = FALLBACK_IMAGE
    
    with open(data_file_path, 'w') as f:
        json.dump(properties, f)
    return jsonify(property)

@app.route('/api/properties/<int:id>', methods=['DELETE'])
def delete_property(id):
    global properties
    properties = [p for p in properties if p['id'] != id]
    with open(data_file_path, 'w') as f:
        json.dump(properties, f)
    return '', 204

if __name__ == '__main__':
    app.run(debug=True)
