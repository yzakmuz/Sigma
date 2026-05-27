// Use relative URLs when served over HTTP, but fallback to localhost when opened locally directly as a file
const API_BASE_URL = window.location.protocol === 'file:' ? 'http://localhost:8000' : '';

let token = localStorage.getItem('token');
let currentUser = localStorage.getItem('currentUser');
let loginTime = localStorage.getItem('loginTime');

let isExpired = false;

// 1. Check local loginTime tracker (20 hours = 20 * 60 * 60 * 1000 ms)
if (loginTime && (Date.now() - parseInt(loginTime) > 20 * 60 * 60 * 1000)) {
    isExpired = true;
} 
// 2. Check JWT expiration directly (covers users logged in before tracking was added)
else if (token) {
    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (payload.exp && (payload.exp * 1000 < Date.now())) {
            isExpired = true;
        }
    } catch (e) {
        isExpired = true; // invalid token
    }
}

if (isExpired) {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userId');
    localStorage.removeItem('loginTime');
}

let allLessons = [];

// Try to optionally refresh the token on app load if valid
async function potentiallyRefreshToken() {
    if (!token) return;
    try {
        const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (response.ok) {
            const data = await response.json();
            token = data.access_token;
            localStorage.setItem('token', token);
            localStorage.setItem('loginTime', Date.now().toString());
            console.log('✓ Token successfully automatically refreshed.');
        }
    } catch (err) {
        console.log('Failed backing token refresh', err);
    }
}

// Initialize
function init() {
    updateAuthUI();
    loadLessons();
    checkHealth();
    potentiallyRefreshToken();
}

// Check API health
async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE_URL}/health`);
        if (!response.ok) throw new Error('API not responding');
        console.log('✓ API is healthy');
    } catch (error) {
        console.error('✗ Cannot connect to API. Make sure it\'s running on http://localhost:8000');
        document.getElementById('lessonsList').innerHTML = '<p style="color: #d32f2f; padding: 20px;">Cannot connect to backend API. Please start the server.</p>';
    }
}

// Update auth UI
function updateAuthUI() {
    if (token && currentUser) {
        document.getElementById('authContainer').classList.add('hidden');
        document.getElementById('userInfo').classList.remove('hidden');
        document.getElementById('logoutBtn').classList.remove('hidden');
        document.getElementById('loginBtn').classList.add('hidden');
        document.getElementById('userName').textContent = currentUser;
        document.getElementById('filterContainer').classList.remove('hidden');
    } else {
        document.getElementById('authContainer').classList.remove('hidden');
        document.getElementById('userInfo').classList.add('hidden');
        document.getElementById('logoutBtn').classList.add('hidden');
        document.getElementById('loginBtn').classList.remove('hidden');
        document.getElementById('filterContainer').classList.add('hidden');
    }
}

// Register
async function register() {
    const email = document.getElementById('registerEmail').value;
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    const messageDiv = document.getElementById('registerMessage');

    if (!email || !username || !password) {
        showMessage(messageDiv, 'error', 'Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/signup`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, username, password })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage(messageDiv, 'success', 'Account created! Please login.');
            document.getElementById('registerEmail').value = '';
            document.getElementById('registerUsername').value = '';
            document.getElementById('registerPassword').value = '';
            setTimeout(() => switchTab('login'), 2000);
        } else {
            showMessage(messageDiv, 'error', data.detail || 'Registration failed');
        }
    } catch (error) {
        showMessage(messageDiv, 'error', 'Connection error: ' + error.message);
    }
}

// Login
async function login() {
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;
    const messageDiv = document.getElementById('loginMessage');

    if (!email || !password) {
        showMessage(messageDiv, 'error', 'Please fill in all fields');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/auth/signin`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password })
        });

        const data = await response.json();

        if (response.ok) {
            token = data.access_token;
            currentUser = email.split('@')[0];
            localStorage.setItem('token', token);
            localStorage.setItem('currentUser', currentUser);
            localStorage.setItem('loginTime', Date.now().toString());
            console.log('✓ Login successful. Token:', token ? 'present' : 'missing');
            
            // Fetch and store current user ID
            const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (userResponse.ok) {
                const userData = await userResponse.json();
                localStorage.setItem('userId', userData.id);
                console.log('✓ User ID stored:', userData.id);
            }
            
            showMessage(messageDiv, 'success', 'Logged in successfully!');
            updateAuthUI();
            loadLessons();
            setTimeout(() => switchTab('login'), 1500);
        } else {
            showMessage(messageDiv, 'error', data.detail || 'Login failed');
            console.error('✗ Login failed:', data);
        }
    } catch (error) {
        showMessage(messageDiv, 'error', 'Connection error: ' + error.message);
        console.error('✗ Login error:', error);
    }
}

// Logout
function logout() {
    token = null;
    currentUser = null;
    localStorage.removeItem('token');
    localStorage.removeItem('currentUser');
    localStorage.removeItem('userId');
    localStorage.removeItem('loginTime');
    updateAuthUI();
    closeLessonDetail();
    loadLessons();
}

// Load lessons
async function loadLessons() {
    const lessonsList = document.getElementById('lessonsList');
    lessonsList.innerHTML = '<div class="loading"><div class="spinner"></div>Loading lessons...</div>';

    try {
        const response = await fetch(`${API_BASE_URL}/lessons`);
        if (!response.ok) throw new Error('Failed to load lessons');

        allLessons = await response.json();
        displayLessons(allLessons);
    } catch (error) {
        lessonsList.innerHTML = `<p style="color: #d32f2f; padding: 20px;">Error loading lessons: ${error.message}</p>`;
    }
}

// Display lessons
function displayLessons(lessons) {
    const lessonsList = document.getElementById('lessonsList');

    if (lessons.length === 0) {
        lessonsList.innerHTML = '<p style="color: #999; padding: 20px;">No lessons found</p>';
        return;
    }

    lessonsList.innerHTML = lessons.map(lesson => `
        <div class="lesson-card" onclick="viewLesson('${lesson.id}')">
            <h4>${lesson.title}</h4>
            <p>${lesson.description}</p>
            <div class="lesson-meta">
                <span class="badge badge-topic">${lesson.topic.toUpperCase()}</span>
                <span class="badge badge-level">${lesson.level.toUpperCase()}</span>
                <span style="color: #999;">📚 ${lesson.problems.length} problems</span>
            </div>
        </div>
    `).join('');
}

// View lesson detail
function viewLesson(lessonId) {
    const lesson = allLessons.find(l => l.id === lessonId);
    if (!lesson) return;

    const content = `
        <h2>${lesson.title}</h2>
        <p>${lesson.description}</p>
        <div class="lesson-meta" style="margin: 15px 0;">
            <span class="badge badge-topic">${lesson.topic.toUpperCase()}</span>
            <span class="badge badge-level">${lesson.level.toUpperCase()}</span>
        </div>
        <small style="color: #999;">Created: ${new Date(lesson.created_at).toLocaleDateString()}</small>
        
        <div class="problems-list">
            <h3>📝 Problems (${lesson.problems.length})</h3>
            ${lesson.problems.map((problem, idx) => `
                <div id="problem-${problem.id}" class="problem-interactive">
                    <div class="problem-header">
                        <div class="problem-label">#${idx + 1} - ${problem.difficulty.toUpperCase()}</div>
                        <div class="attempt-counter" id="attempts-${problem.id}">Attempt: 1</div>
                    </div>
                    
                    <div class="problem-question">
                        <strong>Question:</strong>
                        <p>${problem.question}</p>
                    </div>
                    
                    <div class="feedback" id="feedback-${problem.id}"></div>
                    
                    <div class="hint-section" id="hint-${problem.id}">
                        <strong>💡 Hint:</strong>
                        ${problem.hint}
                    </div>
                    
                    <div class="explanation-section" id="explanation-${problem.id}">
                        <strong>📖 Explanation:</strong>
                        <div id="explanation-text-${problem.id}"></div>
                    </div>
                    
                    <div class="answer-revealed" id="answer-${problem.id}">
                        <strong>✓ Correct Answer:</strong>
                        <div>${problem.answer}</div>
                    </div>
                    
                    <div class="problem-input-section" id="input-section-${problem.id}">
                        <div class="input-group">
                            <input type="text" class="problem-answer" id="answer-input-${problem.id}" 
                                   placeholder="Enter your answer...">
                            <button class="btn-submit" id="submit-btn-${problem.id}" onclick="submitAnswer('${problem.id}', '${lesson.id}', this)">
                                Submit
                            </button>
                            <button class="btn-giveup" onclick="revealAnswer('${problem.id}')">
                                Give Up?
                            </button>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    document.getElementById('lessonDetailContent').innerHTML = content;
    document.getElementById('lessonsContainer').classList.add('hidden');
    document.getElementById('lessonDetailContainer').classList.remove('hidden');
    
    // Load attempts history for all problems if logged in
    if (token) {
        lesson.problems.forEach(problem => loadAttemptHistory(problem.id));
    }
}

// Close lesson detail
function closeLessonDetail() {
    document.getElementById('lessonsContainer').classList.remove('hidden');
    document.getElementById('lessonDetailContainer').classList.add('hidden');
}

// Filter lessons
function filterLessons() {
    const topic = document.getElementById('topicFilter').value;
    const level = document.getElementById('levelFilter').value;

    const filtered = allLessons.filter(lesson => {
        return (!topic || lesson.topic === topic) &&
               (!level || lesson.level === level);
    });

    displayLessons(filtered);
}

// Reset filters
function resetFilters() {
    document.getElementById('topicFilter').value = '';
    document.getElementById('levelFilter').value = '';
    displayLessons(allLessons);
}

// Switch auth tab
function switchTab(tab) {
    document.querySelectorAll('.form-tab').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.form-content').forEach(form => form.classList.remove('active'));
    
    if (tab === 'login') {
        document.querySelectorAll('.form-tab')[0].classList.add('active');
        document.getElementById('loginForm').classList.add('active');
    } else {
        document.querySelectorAll('.form-tab')[1].classList.add('active');
        document.getElementById('registerForm').classList.add('active');
    }
}

// Scroll to auth
function scrollToAuth() {
    document.querySelector('.auth-form').scrollIntoView({ behavior: 'smooth' });
}

// Show message
function showMessage(element, type, text) {
    element.className = `message ${type}`;
    element.textContent = text;
}

// Submit problem answer
async function submitAnswer(problemId, lessonId, buttonElement) {
    // Ensure we have valid token
    if (!token || token === 'null' || token === '') {
        alert('Please login to submit answers');
        return;
    }

    const answerInput = document.getElementById(`answer-input-${problemId}`);
    const submittedAnswer = answerInput.value.trim();

    if (!submittedAnswer) {
        alert('Please enter an answer');
        return;
    }

    const submitBtn = buttonElement;
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    try {
        const response = await fetch(`${API_BASE_URL}/problems/${problemId}/submit`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ problem_id: problemId, submitted_answer: submittedAnswer })
        });

        const data = await response.json();

        if (response.ok) {
            const feedbackDiv = document.getElementById(`feedback-${problemId}`);
            feedbackDiv.classList.add('show');
            feedbackDiv.textContent = `✓ ${data.feedback}`;
            
            if (data.is_correct) {
                feedbackDiv.classList.add('correct');
                feedbackDiv.classList.remove('incorrect');
                // Show explanation if correct
                if (data.explanation) {
                    const explanationDiv = document.getElementById(`explanation-${problemId}`);
                    explanationDiv.classList.add('show');
                    document.getElementById(`explanation-text-${problemId}`).textContent = data.explanation;
                }
            } else {
                feedbackDiv.classList.add('incorrect');
                feedbackDiv.classList.remove('correct');
            }

            // Update attempt counter
            document.getElementById(`attempts-${problemId}`).textContent = 
                `Attempt: ${data.attempt_number}`;
            
            // Clear input
            answerInput.value = '';
        } else {
            alert('Error: ' + (data.detail || 'Failed to submit answer'));
        }
    } catch (error) {
        alert('Connection error: ' + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.textContent = 'Submit';
    }
}

// Reveal answer when user gives up
async function revealAnswer(problemId) {
    if (!token) {
        alert('Please login to reveal answers');
        return;
    }

    const answerDiv = document.getElementById(`answer-${problemId}`);
    const inputSection = document.getElementById(`input-section-${problemId}`);
    const answerInput = document.getElementById(`answer-input-${problemId}`);
    
    answerDiv.classList.add('show');
    inputSection.innerHTML = '<p style="color: #999; font-style: italic;">You gave up on this problem. Try the next one!</p>';
    
    // Hide hint when answer is revealed
    document.getElementById(`hint-${problemId}`).classList.remove('show');
}

// Load attempt history for a problem
async function loadAttemptHistory(problemId) {
    if (!token) return;

    try {
        const userId = localStorage.getItem('userId');
        if (!userId) return;

        const response = await fetch(
            `${API_BASE_URL}/users/${userId}/attempts?problem_id=${problemId}&limit=1`,
            {
                headers: { 'Authorization': `Bearer ${token}` }
            }
        );

        if (response.ok) {
            const attempts = await response.json();
            if (attempts.length > 0) {
                const lastAttempt = attempts[0];
                document.getElementById(`attempts-${problemId}`).textContent = 
                    `Attempt: ${lastAttempt.attempt_number}`;
            }
        }
    } catch (error) {
        console.error('Error loading attempt history:', error);
    }
}

// Start
init();