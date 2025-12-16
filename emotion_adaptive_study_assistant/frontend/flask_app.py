"""
Flask Frontend - Emotion-Adaptive Study Assistant
-------------------------------------------------
Web-based UI for the study assistant.
Based on the design from study_server_web.py.
"""

from flask import Flask, render_template_string, jsonify, request
from flask_cors import CORS
import requests
import threading
import time

app = Flask(__name__)
CORS(app)

# Backend API URL
API_BASE_URL = "http://localhost:8000/api"

# ============================================================
# STUDY MATERIALS - Sample content for demonstration
# ============================================================

STUDY_TOPICS = {
    "python_basics": {
        "name": "Python Basics",
        "materials": [
            {
                "id": "py_1",
                "title": "Variables and Data Types",
                "difficulty": "Easy",
                "content": """Variables in Python are containers for storing data values. 
                
Unlike other programming languages, Python has no command for declaring a variable. A variable is created the moment you first assign a value to it.

**Data Types:**
- **int**: Integer numbers (e.g., 42, -17)
- **float**: Decimal numbers (e.g., 3.14, -0.001)
- **str**: Text strings (e.g., "Hello")
- **bool**: Boolean values (True, False)
- **list**: Ordered collection [1, 2, 3]
- **dict**: Key-value pairs {"name": "John"}""",
                "example": "x = 5          # int\\ny = 3.14       # float\\nname = 'Alice' # str\\nis_valid = True # bool"
            },
            {
                "id": "py_2",
                "title": "Control Flow - If/Else",
                "difficulty": "Easy",
                "content": """Control flow statements determine the order in which code executes.

**If Statement**: Execute code only if a condition is true.
**Elif**: Check additional conditions if previous ones are false.
**Else**: Execute code when no conditions are true.""",
                "example": "age = 18\\n\\nif age < 13:\\n    print('Child')\\nelif age < 20:\\n    print('Teenager')\\nelse:\\n    print('Adult')"
            },
            {
                "id": "py_3",
                "title": "Loops - For and While",
                "difficulty": "Medium",
                "content": """Loops allow you to repeat code multiple times.

**For Loop**: Iterate over a sequence (list, tuple, string, etc.)
**While Loop**: Repeat while a condition is true

**Important**: Avoid infinite loops by ensuring the condition eventually becomes false.""",
                "example": "# For loop\\nfor i in range(5):\\n    print(i)\\n\\n# While loop\\ncount = 0\\nwhile count < 5:\\n    print(count)\\n    count += 1"
            }
        ]
    },
    "data_structures": {
        "name": "Data Structures",
        "materials": [
            {
                "id": "ds_1",
                "title": "Arrays and Lists",
                "difficulty": "Easy",
                "content": """Arrays (called Lists in Python) are ordered collections of items.

**Key Operations:**
- Access: O(1) - Get item by index
- Search: O(n) - Find item by value
- Insert/Delete at end: O(1) amortized
- Insert/Delete at beginning: O(n)""",
                "example": "fruits = ['apple', 'banana', 'cherry']\\nprint(fruits[0])  # 'apple'\\nfruits.append('date')\\nfruits.remove('banana')"
            },
            {
                "id": "ds_2",
                "title": "Hash Tables / Dictionaries",
                "difficulty": "Medium",
                "content": """Hash tables provide O(1) average-case lookup, insert, and delete.

**How it works:**
1. Key is passed through a hash function
2. Hash determines the bucket/index
3. Value is stored at that location

**Collision Handling**: Chaining or Open Addressing""",
                "example": "student = {\\n    'name': 'Alice',\\n    'age': 20,\\n    'grades': [90, 85, 92]\\n}\\nprint(student['name'])  # 'Alice'\\nstudent['major'] = 'CS'  # Add new key"
            },
            {
                "id": "ds_3",
                "title": "Stacks and Queues",
                "difficulty": "Medium",
                "content": """**Stack**: LIFO (Last In, First Out)
- Push: Add to top
- Pop: Remove from top
- Use cases: Undo functionality, parsing expressions

**Queue**: FIFO (First In, First Out)  
- Enqueue: Add to back
- Dequeue: Remove from front
- Use cases: Task scheduling, BFS""",
                "example": "# Stack using list\\nstack = []\\nstack.append(1)  # push\\nstack.append(2)\\nstack.pop()     # returns 2\\n\\n# Queue using deque\\nfrom collections import deque\\nqueue = deque()\\nqueue.append(1)  # enqueue\\nqueue.popleft()  # dequeue"
            }
        ]
    },
    "algorithms": {
        "name": "Algorithms",
        "materials": [
            {
                "id": "algo_1",
                "title": "Binary Search",
                "difficulty": "Easy",
                "content": """Binary Search finds an item in a SORTED array in O(log n) time.

**Algorithm:**
1. Start with middle element
2. If target equals middle, found!
3. If target < middle, search left half
4. If target > middle, search right half
5. Repeat until found or array exhausted""",
                "example": "def binary_search(arr, target):\\n    left, right = 0, len(arr) - 1\\n    while left <= right:\\n        mid = (left + right) // 2\\n        if arr[mid] == target:\\n            return mid\\n        elif arr[mid] < target:\\n            left = mid + 1\\n        else:\\n            right = mid - 1\\n    return -1"
            },
            {
                "id": "algo_2",
                "title": "Sorting Algorithms",
                "difficulty": "Medium",
                "content": """**Common Sorting Algorithms:**

| Algorithm | Time (Avg) | Time (Worst) | Space |
|-----------|------------|--------------|-------|
| Bubble Sort | O(n²) | O(n²) | O(1) |
| Merge Sort | O(n log n) | O(n log n) | O(n) |
| Quick Sort | O(n log n) | O(n²) | O(log n) |
| Heap Sort | O(n log n) | O(n log n) | O(1) |

**For interviews**: Know Merge Sort and Quick Sort well!""",
                "example": "def merge_sort(arr):\\n    if len(arr) <= 1:\\n        return arr\\n    mid = len(arr) // 2\\n    left = merge_sort(arr[:mid])\\n    right = merge_sort(arr[mid:])\\n    return merge(left, right)"
            },
            {
                "id": "algo_3",
                "title": "Dynamic Programming",
                "difficulty": "Hard",
                "content": """Dynamic Programming solves complex problems by breaking them into overlapping subproblems.

**Key Concepts:**
1. **Optimal Substructure**: Solution can be built from subproblem solutions
2. **Overlapping Subproblems**: Same subproblems solved multiple times

**Approaches:**
- Top-down (Memoization): Recursive with caching
- Bottom-up (Tabulation): Iterative, build solution from base cases""",
                "example": "# Fibonacci with memoization\\ndef fib(n, memo={}):\\n    if n in memo:\\n        return memo[n]\\n    if n <= 1:\\n        return n\\n    memo[n] = fib(n-1, memo) + fib(n-2, memo)\\n    return memo[n]"
            }
        ]
    }
}

# ============================================================
# EMOTION CONFIGURATION
# ============================================================

EMOTION_CONFIG = {
    "confused": {"emoji": "🤔", "label": "Confused", "color": "#f59e0b"},
    "overwhelmed": {"emoji": "😵‍💫", "label": "Overwhelmed", "color": "#f97316"},
    "frustrated": {"emoji": "😤", "label": "Frustrated", "color": "#ef4444"},
    "bored": {"emoji": "😴", "label": "Bored", "color": "#a855f7"},
    "curious": {"emoji": "🧠✨", "label": "Curious", "color": "#3b82f6"},
    "anxious": {"emoji": "😟", "label": "Anxious", "color": "#eab308"},
    "confident": {"emoji": "😎", "label": "Confident", "color": "#22c55e"},
    "focused": {"emoji": "🎯", "label": "Focused", "color": "#06b6d4"}
}

# ============================================================
# GLOBAL STATE
# ============================================================

current_topic = None
current_material = None
response_history = []
response_lock = threading.Lock()
study_start_time = None

# ============================================================
# HTML TEMPLATE
# ============================================================

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Emotion-Adaptive Study Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            color: #e4e4e7;
        }
        
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            text-align: center;
            padding: 30px 0;
            border-bottom: 1px solid rgba(255,255,255,0.1);
            margin-bottom: 30px;
        }
        
        header h1 {
            font-size: 2.5rem;
            background: linear-gradient(90deg, #06b6d4, #3b82f6, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 10px;
        }
        
        header p {
            color: #a1a1aa;
            font-size: 1.1rem;
        }
        
        .control-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            background: rgba(0,0,0,0.3);
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .detection-controls {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .btn {
            padding: 10px 20px;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.95rem;
            transition: all 0.2s;
        }
        
        .btn-primary {
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            color: white;
        }
        
        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(6, 182, 212, 0.4);
        }
        
        .btn-danger {
            background: rgba(239, 68, 68, 0.2);
            border: 1px solid #ef4444;
            color: #ef4444;
        }
        
        .btn-danger:hover {
            background: rgba(239, 68, 68, 0.3);
        }
        
        .emotion-display {
            display: flex;
            align-items: center;
            gap: 15px;
            padding: 10px 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
        }
        
        .emotion-icon {
            font-size: 2rem;
        }
        
        .emotion-info {
            text-align: left;
        }
        
        .emotion-label {
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .confidence-bar {
            width: 100px;
            height: 6px;
            background: rgba(255,255,255,0.1);
            border-radius: 3px;
            margin-top: 5px;
            overflow: hidden;
        }
        
        .confidence-fill {
            height: 100%;
            border-radius: 3px;
            transition: width 0.3s;
        }
        
        .main-content {
            display: grid;
            grid-template-columns: 280px 1fr 350px;
            gap: 20px;
        }
        
        .sidebar {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            height: fit-content;
        }
        
        .sidebar h2 {
            font-size: 1.2rem;
            margin-bottom: 15px;
            color: #06b6d4;
        }
        
        .topic-btn {
            display: block;
            width: 100%;
            padding: 12px 16px;
            margin-bottom: 10px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 8px;
            color: #e4e4e7;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
            font-size: 0.95rem;
        }
        
        .topic-btn:hover {
            background: rgba(6, 182, 212, 0.2);
            border-color: #06b6d4;
        }
        
        .topic-btn.active {
            background: rgba(6, 182, 212, 0.3);
            border-color: #06b6d4;
        }
        
        .material-list {
            margin-top: 20px;
            padding-top: 20px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .material-btn {
            display: block;
            width: 100%;
            padding: 10px 12px;
            margin-bottom: 8px;
            background: transparent;
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 6px;
            color: #a1a1aa;
            cursor: pointer;
            transition: all 0.2s;
            text-align: left;
            font-size: 0.85rem;
        }
        
        .material-btn:hover {
            background: rgba(255,255,255,0.05);
            color: #e4e4e7;
        }
        
        .material-btn.active {
            background: rgba(59, 130, 246, 0.2);
            border-color: #3b82f6;
            color: #e4e4e7;
        }
        
        .difficulty {
            font-size: 0.7rem;
            padding: 2px 6px;
            border-radius: 4px;
            margin-left: 8px;
            float: right;
        }
        
        .difficulty.Easy { background: #22c55e33; color: #22c55e; }
        .difficulty.Medium { background: #f59e0b33; color: #f59e0b; }
        .difficulty.Hard { background: #ef444433; color: #ef4444; }
        
        .content-area {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 25px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        
        .content-area h2 {
            font-size: 1.5rem;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .study-content {
            color: #d4d4d8;
            line-height: 1.8;
        }
        
        .study-content p {
            margin-bottom: 15px;
        }
        
        .code-block {
            background: rgba(0,0,0,0.4);
            border-radius: 8px;
            padding: 15px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            color: #86efac;
            margin: 15px 0;
            border-left: 3px solid #3b82f6;
        }
        
        .response-panel {
            background: rgba(255,255,255,0.05);
            border-radius: 16px;
            padding: 20px;
            border: 1px solid rgba(255,255,255,0.1);
            height: fit-content;
            max-height: 600px;
            overflow-y: auto;
        }
        
        .response-panel h2 {
            font-size: 1.1rem;
            margin-bottom: 15px;
            color: #8b5cf6;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .response-item {
            background: rgba(0,0,0,0.2);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            border-left: 4px solid;
            animation: slideIn 0.3s ease-out;
        }
        
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        
        .response-header {
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 10px;
            font-weight: 600;
            font-size: 0.9rem;
        }
        
        .response-text {
            color: #d4d4d8;
            line-height: 1.5;
            font-size: 0.9rem;
        }
        
        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: #71717a;
        }
        
        .empty-state .icon {
            font-size: 3rem;
            margin-bottom: 15px;
        }
        
        
        .timer {
            font-size: 0.9rem;
            color: #71717a;
        }
        
        .timer span {
            color: #06b6d4;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>🎓 Emotion-Adaptive Study Assistant</h1>
            <p>AI-powered study companion that automatically detects and adapts to your emotional state via webcam & microphone</p>
        </header>
        
        <div class="control-bar">
            <div class="detection-controls">
                <button class="btn btn-primary" id="startBtn" onclick="startDetection()">
                    📹 Start Detection
                </button>
                <button class="btn btn-danger" id="stopBtn" onclick="stopDetection()" style="display: none;">
                    ⏹ Stop Detection
                </button>
                <div class="timer" id="timer" style="display: none;">
                    Study time: <span id="timerValue">00:00</span>
                </div>
            </div>
            
            <div class="emotion-display" id="emotionDisplay">
                <div class="emotion-icon" id="emotionIcon">🎯</div>
                <div class="emotion-info">
                    <div class="emotion-label" id="emotionLabel">Focused</div>
                    <div class="confidence-bar">
                        <div class="confidence-fill" id="confidenceFill" style="width: 50%; background: #06b6d4;"></div>
                    </div>
                </div>
            </div>
        </div>
        
        <div class="main-content">
            <div class="sidebar">
                <h2>📚 Study Topics</h2>
                <button class="topic-btn" data-topic="python_basics" onclick="selectTopic('python_basics')">
                    🐍 Python Basics
                </button>
                <button class="topic-btn" data-topic="data_structures" onclick="selectTopic('data_structures')">
                    📊 Data Structures
                </button>
                <button class="topic-btn" data-topic="algorithms" onclick="selectTopic('algorithms')">
                    ⚡ Algorithms
                </button>
                
                <div class="material-list" id="materialList">
                    <p style="color: #71717a; font-size: 0.85rem;">Select a topic to see materials</p>
                </div>
                
            </div>
            
            <div class="content-area" id="contentArea">
                <div class="empty-state">
                    <div class="icon">📖</div>
                    <p>Select a topic and material to start studying</p>
                    <p style="font-size: 0.85rem; margin-top: 10px; color: #52525b;">
                        The system will detect your emotions and provide adaptive support
                    </p>
                </div>
            </div>
            
                <div class="response-panel">
                <h2>💬 Adaptive Responses</h2>
                <div id="responses">
                    <div class="empty-state">
                        <div class="icon">🎭</div>
                        <p>Click "Start Detection" to begin</p>
                        <p style="font-size: 0.8rem; margin-top: 8px; color: #52525b;">
                            The system will analyze your facial expressions and voice to detect emotions automatically
                        </p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Configuration
        const API_URL = '/api';
        let isDetecting = false;
        let studyStartTime = null;
        let timerInterval = null;
        let pollInterval = null;
        let currentTopic = null;
        let currentMaterial = null;
        let lastResponseCount = 0;
        
        // Emotion configuration
        const EMOTIONS = {
            confused: { emoji: '🤔', label: 'Confused', color: '#f59e0b' },
            overwhelmed: { emoji: '😵‍💫', label: 'Overwhelmed', color: '#f97316' },
            frustrated: { emoji: '😤', label: 'Frustrated', color: '#ef4444' },
            bored: { emoji: '😴', label: 'Bored', color: '#a855f7' },
            curious: { emoji: '🧠✨', label: 'Curious', color: '#3b82f6' },
            anxious: { emoji: '😟', label: 'Anxious', color: '#eab308' },
            confident: { emoji: '😎', label: 'Confident', color: '#22c55e' },
            focused: { emoji: '🎯', label: 'Focused', color: '#06b6d4' }
        };
        
        // Start emotion detection
        async function startDetection() {
            try {
                const response = await fetch(API_URL + '/detection/start', { method: 'POST' });
                const data = await response.json();
                
                isDetecting = true;
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
                document.getElementById('timer').style.display = 'block';
                
                studyStartTime = Date.now();
                startTimer();
                startPolling();
                
            } catch (error) {
                console.log('Detection start failed, using manual mode');
                // Still show UI even if detection fails (for testing)
                isDetecting = true;
                document.getElementById('startBtn').style.display = 'none';
                document.getElementById('stopBtn').style.display = 'inline-block';
            }
        }
        
        // Stop emotion detection
        async function stopDetection() {
            try {
                await fetch(API_URL + '/detection/stop', { method: 'POST' });
            } catch (error) {
                console.log('Stop detection request failed');
            }
            
            isDetecting = false;
            document.getElementById('startBtn').style.display = 'inline-block';
            document.getElementById('stopBtn').style.display = 'none';
            document.getElementById('timer').style.display = 'none';
            
            stopTimer();
            stopPolling();
        }
        
        // Timer functions
        function startTimer() {
            timerInterval = setInterval(updateTimer, 1000);
        }
        
        function stopTimer() {
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
        }
        
        function updateTimer() {
            const elapsed = Math.floor((Date.now() - studyStartTime) / 1000);
            const minutes = Math.floor(elapsed / 60).toString().padStart(2, '0');
            const seconds = (elapsed % 60).toString().padStart(2, '0');
            document.getElementById('timerValue').textContent = `${minutes}:${seconds}`;
        }
        
        // Polling for emotion updates
        function startPolling() {
            pollInterval = setInterval(pollEmotion, 1000);
        }
        
        function stopPolling() {
            if (pollInterval) {
                clearInterval(pollInterval);
                pollInterval = null;
            }
        }
        
        async function pollEmotion() {
            try {
                // Get current emotion
                const emotionRes = await fetch(API_URL + '/emotion');
                const emotionData = await emotionRes.json();
                updateEmotionDisplay(emotionData);
                
                // Check for interventions
                const interventionRes = await fetch(API_URL + '/intervention');
                const interventionData = await interventionRes.json();
                
                if (interventionData.intervention && interventionData.intervention.message) {
                    addResponse(interventionData.emotion, interventionData.intervention.message);
                }
                
            } catch (error) {
                // Silently fail, will retry
            }
        }
        
        // Update emotion display
        function updateEmotionDisplay(data) {
            const emotion = data.emotion || 'focused';
            const confidence = data.confidence || 0.5;
            const config = EMOTIONS[emotion] || EMOTIONS.focused;
            
            document.getElementById('emotionIcon').textContent = config.emoji;
            document.getElementById('emotionLabel').textContent = config.label;
            document.getElementById('confidenceFill').style.width = `${confidence * 100}%`;
            document.getElementById('confidenceFill').style.background = config.color;
        }
        
        
        // Add response to panel
        function addResponse(emotion, message) {
            if (!message) return;
            
            const config = EMOTIONS[emotion] || EMOTIONS.focused;
            const responsesEl = document.getElementById('responses');
            
            // Clear empty state on first response
            if (responsesEl.querySelector('.empty-state')) {
                responsesEl.innerHTML = '';
            }
            
            const div = document.createElement('div');
            div.className = 'response-item';
            div.style.borderColor = config.color;
            div.innerHTML = `
                <div class="response-header" style="color: ${config.color}">
                    ${config.emoji} ${config.label}
                </div>
                <div class="response-text">${message}</div>
            `;
            
            responsesEl.insertBefore(div, responsesEl.firstChild);
            
            // Keep only last 10 responses
            while (responsesEl.children.length > 10) {
                responsesEl.removeChild(responsesEl.lastChild);
            }
        }
        
        // Topic selection
        async function selectTopic(topic) {
            currentTopic = topic;
            
            // Update button states
            document.querySelectorAll('.topic-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-topic="${topic}"]`).classList.add('active');
            
            // Fetch materials
            const response = await fetch(API_URL + '/materials/' + topic);
            const data = await response.json();
            
            const listEl = document.getElementById('materialList');
            listEl.innerHTML = '<h3 style="font-size: 0.9rem; color: #a1a1aa; margin-bottom: 10px;">Materials</h3>';
            
            data.materials.forEach((m, idx) => {
                const btn = document.createElement('button');
                btn.className = 'material-btn';
                btn.dataset.materialId = m.id;
                btn.innerHTML = `${idx + 1}. ${m.title} <span class="difficulty ${m.difficulty}">${m.difficulty}</span>`;
                btn.onclick = () => selectMaterial(topic, m.id);
                listEl.appendChild(btn);
            });
        }
        
        // Material selection
        async function selectMaterial(topic, materialId) {
            currentMaterial = materialId;
            
            // Update button states
            document.querySelectorAll('.material-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelector(`[data-material-id="${materialId}"]`).classList.add('active');
            
            // Fetch material content
            const response = await fetch(API_URL + '/material/' + topic + '/' + materialId);
            const data = await response.json();
            
            const contentEl = document.getElementById('contentArea');
            contentEl.innerHTML = `
                <h2>📝 ${data.title} <span class="difficulty ${data.difficulty}">${data.difficulty}</span></h2>
                <div class="study-content">
                    ${data.content.split('\\n').map(p => `<p>${p}</p>`).join('')}
                </div>
                <div class="code-block">${data.example}</div>
            `;
        }
    </script>
</body>
</html>
'''

# ============================================================
# FLASK ROUTES
# ============================================================

@app.route('/')
def index():
    """Serve the main study interface."""
    return render_template_string(HTML_TEMPLATE)


@app.route('/api/materials/<topic>')
def get_materials(topic):
    """Get list of materials for a topic."""
    if topic in STUDY_TOPICS:
        return jsonify({
            "name": STUDY_TOPICS[topic]["name"],
            "materials": STUDY_TOPICS[topic]["materials"]
        })
    return jsonify({"error": "Topic not found"}), 404


@app.route('/api/material/<topic>/<material_id>')
def get_material(topic, material_id):
    """Get specific material content."""
    if topic in STUDY_TOPICS:
        for m in STUDY_TOPICS[topic]["materials"]:
            if m["id"] == material_id:
                return jsonify(m)
    return jsonify({"error": "Material not found"}), 404


# ============================================================
# PROXY ROUTES TO BACKEND API
# ============================================================

@app.route('/api/detection/start', methods=['POST'])
def proxy_start_detection():
    """Proxy to backend detection start."""
    try:
        response = requests.post(f"{API_BASE_URL}/detection/start", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/detection/stop', methods=['POST'])
def proxy_stop_detection():
    """Proxy to backend detection stop."""
    try:
        response = requests.post(f"{API_BASE_URL}/detection/stop", timeout=5)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"status": "stopped", "message": "Stopped (backend not responding)"})


@app.route('/api/emotion')
def proxy_get_emotion():
    """Proxy to backend emotion endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/emotion", timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"emotion": "focused", "confidence": 0.5})


@app.route('/api/intervention')
def proxy_get_intervention():
    """Proxy to backend intervention endpoint."""
    try:
        response = requests.get(f"{API_BASE_URL}/intervention", timeout=2)
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"intervention": None, "emotion": "focused"})




# ============================================================
# MAIN
# ============================================================

def main():
    """Run the Flask frontend server."""
    print("\n" + "="*60)
    print("🎓 EMOTION-ADAPTIVE STUDY ASSISTANT")
    print("    Flask Frontend")
    print("="*60)
    print("\n🌐 Open in browser: http://localhost:5002")
    print("📡 Connecting to backend at: http://localhost:8000")
    print("\n   Make sure to run the backend first:")
    print("   python run.py --backend")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)


if __name__ == "__main__":
    main()

