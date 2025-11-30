#!/usr/bin/env python3
"""
Database Browser for Multi-Emulator Launcher
Provides a web interface to view and edit database tables
"""

import sqlite3
import json
from flask import Flask, render_template_string, request, jsonify
from ..database.database_manager import DatabaseManager
import os

app = Flask(__name__)

# Initialize database manager
db_manager = DatabaseManager()

# HTML template for the database browser
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>MEL Database Browser</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .nav {
            text-align: center;
            margin-bottom: 20px;
        }
        .nav button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .nav button:hover {
            background-color: #45a049;
        }
        .nav button.active {
            background-color: #2196F3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
            font-weight: bold;
        }
        tr:nth-child(even) {
            background-color: #f9f9f9;
        }
        .form-group {
            margin: 10px 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-sizing: border-box;
        }
        .btn {
            background-color: #008CBA;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            margin: 5px;
        }
        .btn:hover {
            background-color: #007B9A;
        }
        .btn-danger {
            background-color: #f44336;
        }
        .btn-danger:hover {
            background-color: #d32f2f;
        }
        .btn-success {
            background-color: #4CAF50;
        }
        .btn-success:hover {
            background-color: #45a049;
        }
        .hidden {
            display: none;
        }
        .stats {
            background-color: #e7f3ff;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        .edit-form {
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>MEL Database Browser</h1>
        
        <div class="stats">
            <h3>Database Statistics</h3>
            <p>Platforms: {{ stats.platforms }} | Games: {{ stats.games }} | BIOS Files: {{ stats.bios_files }} | Cores: {{ stats.cores }}</p>
        </div>
        
        <div class="nav">
            <button onclick="showTable('platforms')" class="active" id="btn-platforms">Platforms</button>
            <button onclick="showTable('games')" id="btn-games">Games</button>
            <button onclick="showTable('cores')" id="btn-cores">Cores</button>
            <button onclick="showTable('bios_files')" id="btn-bios_files">BIOS Files</button>
        </div>
        
        <div id="platforms-section">
            <h2>Platforms</h2>
            <button onclick="showAddForm('platforms')" class="btn">Add Platform</button>
            <div id="platforms-form" class="edit-form hidden">
                <h3 id="form-title-platforms">Add Platform</h3>
                <div class="form-group">
                    <label for="platform-name">Name:</label>
                    <input type="text" id="platform-name" required>
                </div>
                <div class="form-group">
                    <label for="platform-normalized_name">Normalized Name:</label>
                    <input type="text" id="platform-normalized_name">
                </div>
                <div class="form-group">
                    <label for="platform-rom_directory">ROM Directory:</label>
                    <input type="text" id="platform-rom_directory">
                </div>
                <div class="form-group">
                    <label for="platform-bios_directory">BIOS Directory:</label>
                    <input type="text" id="platform-bios_directory">
                </div>
                <div class="form-group">
                    <label for="platform-core_path">Core Path:</label>
                    <input type="text" id="platform-core_path">
                </div>
                <div class="form-group">
                    <label for="platform-extension_filter">Extension Filter:</label>
                    <input type="text" id="platform-extension_filter">
                </div>
                <div class="form-group">
                    <label for="platform-total_games">Total Games:</label>
                    <input type="number" id="platform-total_games" value="0">
                </div>
                <div class="form-group">
                    <label for="platform-has_bios">Has BIOS:</label>
                    <select id="platform-has_bios">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
                <button onclick="savePlatform()" class="btn btn-success">Save</button>
                <button onclick="hideForm('platforms')" class="btn">Cancel</button>
            </div>
            <div id="platforms-content"></div>
        </div>
        
        <div id="games-section" class="hidden">
            <h2>Games</h2>
            <button onclick="showAddForm('games')" class="btn">Add Game</button>
            <div id="games-form" class="edit-form hidden">
                <h3 id="form-title-games">Add Game</h3>
                <div class="form-group">
                    <label for="game-platform_id">Platform ID:</label>
                    <input type="number" id="game-platform_id" required>
                </div>
                <div class="form-group">
                    <label for="game-name">Name:</label>
                    <input type="text" id="game-name" required>
                </div>
                <div class="form-group">
                    <label for="game-file_path">File Path:</label>
                    <input type="text" id="game-file_path" required>
                </div>
                <div class="form-group">
                    <label for="game-file_size">File Size:</label>
                    <input type="number" id="game-file_size" value="0">
                </div>
                <div class="form-group">
                    <label for="game-file_hash">File Hash:</label>
                    <input type="text" id="game-file_hash">
                </div>
                <div class="form-group">
                    <label for="game-is_multidisk">Is Multidisk:</label>
                    <select id="game-is_multidisk">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="game-disk_number">Disk Number:</label>
                    <input type="number" id="game-disk_number">
                </div>
                <div class="form-group">
                    <label for="game-total_disks">Total Disks:</label>
                    <input type="number" id="game-total_disks">
                </div>
                <div class="form-group">
                    <label for="game-has_bios">Has BIOS:</label>
                    <select id="game-has_bios">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
                <button onclick="saveGame()" class="btn btn-success">Save</button>
                <button onclick="hideForm('games')" class="btn">Cancel</button>
            </div>
            <div id="games-content"></div>
        </div>
        
        <div id="cores-section" class="hidden">
            <h2>Cores</h2>
            <button onclick="showAddForm('cores')" class="btn">Add Core</button>
            <div id="cores-form" class="edit-form hidden">
                <h3 id="form-title-cores">Add Core</h3>
                <div class="form-group">
                    <label for="core-platform_name">Platform Name:</label>
                    <input type="text" id="core-platform_name" required>
                </div>
                <div class="form-group">
                    <label for="core-core_name">Core Name:</label>
                    <input type="text" id="core-core_name">
                </div>
                <div class="form-group">
                    <label for="core-core_path">Core Path:</label>
                    <input type="text" id="core-core_path">
                </div>
                <div class="form-group">
                    <label for="core-available_cores">Available Cores (JSON array):</label>
                    <textarea id="core-available_cores"></textarea>
                </div>
                <div class="form-group">
                    <label for="core-preferred_core">Preferred Core:</label>
                    <input type="text" id="core-preferred_core">
                </div>
                <button onclick="saveCore()" class="btn btn-success">Save</button>
                <button onclick="hideForm('cores')" class="btn">Cancel</button>
            </div>
            <div id="cores-content"></div>
        </div>
        
        <div id="bios_files-section" class="hidden">
            <h2>BIOS Files</h2>
            <button onclick="showAddForm('bios_files')" class="btn">Add BIOS File</button>
            <div id="bios_files-form" class="edit-form hidden">
                <h3 id="form-title-bios_files">Add BIOS File</h3>
                <div class="form-group">
                    <label for="bios-platform_id">Platform ID:</label>
                    <input type="number" id="bios-platform_id" required>
                </div>
                <div class="form-group">
                    <label for="bios-filename">Filename:</label>
                    <input type="text" id="bios-filename" required>
                </div>
                <div class="form-group">
                    <label for="bios-file_path">File Path:</label>
                    <input type="text" id="bios-file_path" required>
                </div>
                <div class="form-group">
                    <label for="bios-required">Required:</label>
                    <select id="bios-required">
                        <option value="0">No</option>
                        <option value="1">Yes</option>
                    </select>
                </div>
                <div class="form-group">
                    <label for="bios-size">Size:</label>
                    <input type="number" id="bios-size">
                </div>
                <div class="form-group">
                    <label for="bios-md5_hash">MD5 Hash:</label>
                    <input type="text" id="bios-md5_hash">
                </div>
                <button onclick="saveBiosFile()" class="btn btn-success">Save</button>
                <button onclick="hideForm('bios_files')" class="btn">Cancel</button>
            </div>
            <div id="bios_files-content"></div>
        </div>
    </div>

    <script>
        // Track current form being edited
        let currentEditId = null;
        let currentTable = 'platforms';
        
        // Show selected table and hide others
        function showTable(tableName) {
            // Hide all sections
            document.getElementById('platforms-section').classList.add('hidden');
            document.getElementById('games-section').classList.add('hidden');
            document.getElementById('cores-section').classList.add('hidden');
            document.getElementById('bios_files-section').classList.add('hidden');
            
            // Show selected section
            document.getElementById(tableName + '-section').classList.remove('hidden');
            
            // Update active button
            document.querySelectorAll('.nav button').forEach(btn => btn.classList.remove('active'));
            document.getElementById('btn-' + tableName).classList.add('active');
            
            currentTable = tableName;
            
            // Load data for the selected table
            loadTableData(tableName);
        }
        
        // Load data for a specific table
        function loadTableData(tableName) {
            fetch(`/api/${tableName}`)
                .then(response => response.json())
                .then(data => {
                    renderTable(tableName, data);
                })
                .catch(error => console.error('Error loading data:', error));
        }
        
        // Render table with data
        function renderTable(tableName, data) {
            const container = document.getElementById(tableName + '-content');
            
            if (data.length === 0) {
                container.innerHTML = '<p>No data found in this table.</p>';
                return;
            }
            
            // Create table header
            let tableHTML = '<table><thead><tr>';
            if (data.length > 0) {
                Object.keys(data[0]).forEach(key => {
                    tableHTML += `<th>${key}</th>`;
                });
                tableHTML += '<th>Actions</th>';
            }
            tableHTML += '</tr></thead><tbody>';
            
            // Create table rows
            data.forEach(row => {
                tableHTML += '<tr>';
                Object.values(row).forEach(value => {
                    // Format JSON fields
                    let displayValue = value;
                    if (typeof value === 'object' && value !== null) {
                        displayValue = JSON.stringify(value);
                    }
                    tableHTML += `<td>${displayValue}</td>`;
                });
                
                // Add action buttons
                tableHTML += `<td>
                    <button onclick="editRow('${tableName}', ${row.id})" class="btn">Edit</button>
                    <button onclick="deleteRow('${tableName}', ${row.id})" class="btn btn-danger">Delete</button>
                </td>`;
                
                tableHTML += '</tr>';
            });
            
            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;
        }
        
        // Show add form
        function showAddForm(tableName) {
            currentEditId = null;
            document.getElementById('form-title-' + tableName).textContent = 'Add ' + tableName.charAt(0).toUpperCase() + tableName.slice(1);
            document.getElementById(tableName + '-form').classList.remove('hidden');
            
            // Clear form fields
            const formFields = document.querySelectorAll(`#${tableName}-form input, #${tableName}-form select, #${tableName}-form textarea`);
            formFields.forEach(field => {
                if (field.type === 'number') {
                    field.value = field.id.includes('total_games') || field.id.includes('file_size') || field.id.includes('size') ? '0' : '';
                } else if (field.type === 'select-one') {
                    field.selectedIndex = 0;
                } else {
                    field.value = '';
                }
            });
        }
        
        // Edit a row
        function editRow(tableName, id) {
            currentEditId = id;
            document.getElementById('form-title-' + tableName).textContent = 'Edit ' + tableName.charAt(0).toUpperCase() + tableName.slice(1);
            document.getElementById(tableName + '-form').classList.remove('hidden');
            
            // Load row data into form
            fetch(`/api/${tableName}/${id}`)
                .then(response => response.json())
                .then(data => {
                    Object.keys(data).forEach(key => {
                        const field = document.getElementById(`${tableName}-${key}`);
                        if (field) {
                            if (key === 'available_cores' && typeof data[key] === 'object') {
                                field.value = JSON.stringify(data[key]);
                            } else {
                                field.value = data[key];
                            }
                        }
                    });
                })
                .catch(error => console.error('Error loading row:', error));
        }
        
        // Hide form
        function hideForm(tableName) {
            document.getElementById(tableName + '-form').classList.add('hidden');
            currentEditId = null;
        }
        
        // Save platform
        function savePlatform() {
            const platformData = {
                name: document.getElementById('platform-name').value,
                normalized_name: document.getElementById('platform-normalized_name').value,
                rom_directory: document.getElementById('platform-rom_directory').value,
                bios_directory: document.getElementById('platform-bios_directory').value,
                core_path: document.getElementById('platform-core_path').value,
                extension_filter: document.getElementById('platform-extension_filter').value,
                total_games: parseInt(document.getElementById('platform-total_games').value),
                has_bios: parseInt(document.getElementById('platform-has_bios').value)
            };
            
            const url = currentEditId ? `/api/platforms/${currentEditId}` : '/api/platforms';
            const method = currentEditId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(platformData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTableData('platforms');
                hideForm('platforms');
            })
            .catch(error => console.error('Error saving platform:', error));
        }
        
        // Save game
        function saveGame() {
            const gameData = {
                platform_id: parseInt(document.getElementById('game-platform_id').value),
                name: document.getElementById('game-name').value,
                file_path: document.getElementById('game-file_path').value,
                file_size: parseInt(document.getElementById('game-file_size').value),
                file_hash: document.getElementById('game-file_hash').value,
                is_multidisk: parseInt(document.getElementById('game-is_multidisk').value),
                disk_number: document.getElementById('game-disk_number').value ? parseInt(document.getElementById('game-disk_number').value) : null,
                total_disks: document.getElementById('game-total_disks').value ? parseInt(document.getElementById('game-total_disks').value) : null,
                has_bios: parseInt(document.getElementById('game-has_bios').value)
            };
            
            const url = currentEditId ? `/api/games/${currentEditId}` : '/api/games';
            const method = currentEditId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(gameData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTableData('games');
                hideForm('games');
            })
            .catch(error => console.error('Error saving game:', error));
        }
        
        // Save core
        function saveCore() {
            const coreData = {
                platform_name: document.getElementById('core-platform_name').value,
                core_name: document.getElementById('core-core_name').value,
                core_path: document.getElementById('core-core_path').value,
                available_cores: document.getElementById('core-available_cores').value ? JSON.parse(document.getElementById('core-available_cores').value) : null,
                preferred_core: document.getElementById('core-preferred_core').value
            };
            
            const url = currentEditId ? `/api/cores/${currentEditId}` : '/api/cores';
            const method = currentEditId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(coreData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTableData('cores');
                hideForm('cores');
            })
            .catch(error => console.error('Error saving core:', error));
        }
        
        // Save BIOS file
        function saveBiosFile() {
            const biosData = {
                platform_id: parseInt(document.getElementById('bios-platform_id').value),
                filename: document.getElementById('bios-filename').value,
                file_path: document.getElementById('bios-file_path').value,
                required: parseInt(document.getElementById('bios-required').value),
                size: document.getElementById('bios-size').value ? parseInt(document.getElementById('bios-size').value) : null,
                md5_hash: document.getElementById('bios-md5_hash').value
            };
            
            const url = currentEditId ? `/api/bios_files/${currentEditId}` : '/api/bios_files';
            const method = currentEditId ? 'PUT' : 'POST';
            
            fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(biosData)
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                loadTableData('bios_files');
                hideForm('bios_files');
            })
            .catch(error => console.error('Error saving BIOS file:', error));
        }
        
        // Delete a row
        function deleteRow(tableName, id) {
            if (confirm('Are you sure you want to delete this record?')) {
                fetch(`/api/${tableName}/${id}`, {
                    method: 'DELETE'
                })
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                    loadTableData(tableName);
                })
                .catch(error => console.error('Error deleting row:', error));
            }
        }
        
        // Load platforms by default
        window.onload = function() {
            loadTableData('platforms');
        };
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    stats = db_manager.get_database_stats()
    return render_template_string(HTML_TEMPLATE, stats=stats)

@app.route('/api/<table_name>')
def get_table_data(table_name):
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        result = [dict(row) for row in rows]
        conn.close()
        return jsonify(result)
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/<table_name>/<int:record_id>')
def get_record(table_name, record_id):
    conn = sqlite3.connect(db_manager.db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    try:
        cursor.execute(f"SELECT * FROM {table_name} WHERE id = ?", (record_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return jsonify(dict(row))
        else:
            return jsonify({'error': 'Record not found'}), 404
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/platforms', methods=['POST'])
def add_platform():
    data = request.json
    try:
        platform_id = db_manager.add_platform(
            name=data['name'],
            normalized_name=data.get('normalized_name'),
            rom_directory=data.get('rom_directory'),
            bios_directory=data.get('bios_directory'),
            core_path=data.get('core_path'),
            extension_filter=data.get('extension_filter'),
        )
        # Update additional fields that aren't handled by add_platform
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE platforms 
            SET total_games = ?, has_bios = ?
            WHERE id = ?
        """, (data.get('total_games', 0), data.get('has_bios', 0), platform_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Platform added successfully', 'id': platform_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/platforms/<int:platform_id>', methods=['PUT'])
def update_platform(platform_id):
    data = request.json
    try:
        db_manager.add_platform(
            name=data['name'],
            normalized_name=data.get('normalized_name'),
            rom_directory=data.get('rom_directory'),
            bios_directory=data.get('bios_directory'),
            core_path=data.get('core_path'),
            extension_filter=data.get('extension_filter'),
        )
        # Update additional fields
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE platforms 
            SET total_games = ?, has_bios = ?
            WHERE id = ?
        """, (data.get('total_games', 0), data.get('has_bios', 0), platform_id))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Platform updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM platforms WHERE id = ?", (platform_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Platform deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/games', methods=['POST'])
def add_game():
    data = request.json
    try:
        game_id = db_manager.add_game(
            platform_id=data['platform_id'],
            name=data['name'],
            file_path=data['file_path'],
            file_size=data.get('file_size', 0),
            file_hash=data.get('file_hash'),
            is_multidisk=data.get('is_multidisk', 0),
            disk_number=data.get('disk_number'),
            total_disks=data.get('total_disks'),
            has_bios=data.get('has_bios', 0)
        )
        return jsonify({'message': 'Game added successfully', 'id': game_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/games/<int:game_id>', methods=['PUT'])
def update_game(game_id):
    data = request.json
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE games 
            SET platform_id = ?, name = ?, file_path = ?, file_size = ?, 
                file_hash = ?, is_multidisk = ?, disk_number = ?, 
                total_disks = ?, has_bios = ?
            WHERE id = ?
        """, (
            data['platform_id'], data['name'], data['file_path'], 
            data.get('file_size', 0), data.get('file_hash'), 
            data.get('is_multidisk', 0), data.get('disk_number'), 
            data.get('total_disks'), data.get('has_bios', 0), game_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Game updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/games/<int:game_id>', methods=['DELETE'])
def delete_game(game_id):
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM games WHERE id = ?", (game_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Game deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/cores', methods=['POST'])
def add_core():
    data = request.json
    try:
        db_manager.add_core_info(
            platform_name=data['platform_name'],
            core_name=data.get('core_name'),
            core_path=data.get('core_path'),
            available_cores=data.get('available_cores'),
            preferred_core=data.get('preferred_core')
        )
        return jsonify({'message': 'Core added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/cores/<int:core_id>', methods=['PUT'])
def update_core(core_id):
    data = request.json
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        # Get the platform name since it's the primary key for the cores table
        cursor.execute("SELECT platform_name FROM cores WHERE id = ?", (core_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Core not found'}), 404
        
        platform_name = result[0]
        
        # Update the core info
        cursor.execute("""
            UPDATE cores 
            SET core_name = ?, core_path = ?, available_cores = ?, preferred_core = ?
            WHERE platform_name = ?
        """, (
            data.get('core_name'), data.get('core_path'), 
            json.dumps(data.get('available_cores')) if data.get('available_cores') else None,
            data.get('preferred_core'), platform_name
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Core updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/cores/<int:core_id>', methods=['DELETE'])
def delete_core(core_id):
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        # Get the platform name to delete by primary key
        cursor.execute("SELECT platform_name FROM cores WHERE id = ?", (core_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': 'Core not found'}), 404
        
        platform_name = result[0]
        cursor.execute("DELETE FROM cores WHERE platform_name = ?", (platform_name,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Core deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/bios_files', methods=['POST'])
def add_bios_file():
    data = request.json
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO bios_files (platform_id, filename, file_path, required, size, md5_hash)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            data['platform_id'], data['filename'], data['file_path'],
            data.get('required', 0), data.get('size'), data.get('md5_hash')
        ))
        bios_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return jsonify({'message': 'BIOS file added successfully', 'id': bios_id})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/bios_files/<int:bios_id>', methods=['PUT'])
def update_bios_file(bios_id):
    data = request.json
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE bios_files 
            SET platform_id = ?, filename = ?, file_path = ?, 
                required = ?, size = ?, md5_hash = ?
            WHERE id = ?
        """, (
            data['platform_id'], data['filename'], data['file_path'],
            data.get('required', 0), data.get('size'), 
            data.get('md5_hash'), bios_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'message': 'BIOS file updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/bios_files/<int:bios_id>', methods=['DELETE'])
def delete_bios_file(bios_id):
    try:
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM bios_files WHERE id = ?", (bios_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'BIOS file deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    # Set debug to False in production
    app.run(host='0.0.0.0', port=5000, debug=False)