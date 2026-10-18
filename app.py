from flask import Flask, request, jsonify
import subprocess
import os
import tempfile

app = Flask(__name__)

@app.route('/api/deobf', methods=['POST'])
def deobfuscate():
    data = request.get_json()
    if not data or 'script' not in data:
        return jsonify({"error": "Nu ai trimis niciun script"}), 400
    
    script_content = data['script']
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".lua", mode="w", encoding="utf-8") as temp_in:
        temp_in.write(script_content)
        temp_in_path = temp_in.name
        
    temp_out_path = temp_in_path + ".out.lua"
    
    try:
        result = subprocess.run(
            ['python', 'pol.py', temp_in_path, '-o', temp_out_path], 
            capture_output=True, text=True, timeout=60
        )
        
        if os.path.exists(temp_out_path):
            with open(temp_out_path, 'r', encoding='utf-8') as f:
                clean_code = f.read()
            return jsonify({"success": True, "code": clean_code})
        else:
            return jsonify({"error": "Deobfuscarea a eșuat", "details": result.stderr}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if os.path.exists(temp_in_path): os.remove(temp_in_path)
        if os.path.exists(temp_out_path): os.remove(temp_out_path)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
