// RAG Application - Simplified and Working Version
let projects = [];
const categories = ["All", "Research", "Documentation", "Knowledge Base", "Personal", "Business"];

// State management
let currentFilter = 'All';
let currentSearch = '';
let filteredProjects = [];
let currentProjectId = null;
let chatHistory = [];

// DOM elements
const projectsGrid = document.getElementById('projects-grid');
const filterButtons = document.getElementById('filter-buttons');
const searchInput = document.getElementById('search-input');
const homePage = document.getElementById('home-page');
const chatPage = document.getElementById('chat-page');
const backButton = document.getElementById('back-button');
const noResults = document.getElementById('no-results');
const themeToggle = document.getElementById('theme-toggle');
const themeIcon = document.getElementById('theme-icon');
const header = document.querySelector('.header');

// Modal elements
const createProjectModal = document.getElementById('create-project-modal');
const createProjectBtn = document.getElementById('create-project-btn');
const refreshProjectsBtn = document.getElementById('refresh-projects-btn');
const closeModal = document.getElementById('close-modal');
const cancelCreate = document.getElementById('cancel-create');
const createProjectForm = document.getElementById('create-project-form');
const projectFiles = document.getElementById('project-files');
const selectedFilesContainer = document.getElementById('selected-files');

// Chat elements
const chatProjectTitle = document.getElementById('chat-project-title');
const chatProjectSubtitle = document.getElementById('chat-project-subtitle');
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const clearChatBtn = document.getElementById('clear-chat-btn');
const typingIndicator = document.getElementById('typing-indicator');

// Initialize the application
function init() {
    console.log('Initializing RAG Application...');
    
    // Initialize theme first (most important for user experience)
    initTheme();
    
    // Initialize all basic functionality
    renderFilterButtons();
    renderProjects();
    attachEventListeners();
    initChatInput();
    
    console.log('RAG Application initialized successfully');
}

// Theme Management
function initTheme() {
    const savedTheme = localStorage.getItem('rag-theme') || 'dark';  // Default to dark
    setTheme(savedTheme);
}

function setTheme(theme) {
    document.documentElement.setAttribute('data-color-scheme', theme);
    if (themeIcon) {
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    }
    localStorage.setItem('rag-theme', theme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-color-scheme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
}

// Project Management
function loadProjectsFromBackend() {
    // Simple function to load projects from backend
    fetch('http://localhost:5001/api/list-projects')
        .then(response => response.json())
        .then(data => {
            projects = data.projects || [];
            filteredProjects = [...projects];
            renderProjects();
            console.log('✅ Projects loaded from backend:', projects.length);
        })
        .catch(error => {
            console.log('⚠️ Could not load from backend:', error.message);
            // Keep existing projects or use empty array
            projects = projects || [];
            filteredProjects = [...projects];
            renderProjects();
        });
}

function createNewProject(projectData) {
    // Use normalized name as ID to match backend folder structure
    const normalizedName = projectData.name.toLowerCase().replace(/[^a-z0-9]/g, '-');
    
    const newProject = {
        id: normalizedName,
        name: projectData.name,
        description: projectData.description,
        category: projectData.category,
        createdDate: new Date().toISOString().split('T')[0],
        documentCount: projectData.files ? projectData.files.length : 0,
        lastChatDate: null,
        filePaths: projectData.filePaths || [],
        folderName: normalizedName
    };
    
    console.log('Creating project:', newProject);
    
    // Add to projects array
    projects.unshift(newProject);
    filterProjects();
    hideCreateProjectModal();
    
    console.log('✅ Project created successfully:', newProject);
}

// UI Rendering
function renderFilterButtons() {
    if (!filterButtons) return;
    
    filterButtons.innerHTML = categories.map(category => 
        `<button class="filter-btn ${category === currentFilter ? 'active' : ''}" 
                 data-category="${category}">
            ${category}
        </button>`
    ).join('');
}

function renderProjects() {
    if (!projectsGrid) return;
    
    if (filteredProjects.length === 0) {
        projectsGrid.innerHTML = '';
        if (noResults) {
            noResults.classList.remove('hidden');
        }
        return;
    }
    
    if (noResults) {
        noResults.classList.add('hidden');
    }
    
    projectsGrid.innerHTML = filteredProjects.map(project => `
        <div class="project-card" data-project-id="${project.id}">
            <div class="project-card__header">
                <div class="project-card__category">${project.category}</div>
                <div class="project-card__actions">
                    <button class="project-action-btn" data-action="chat" title="Open Chat">💬</button>
                    <button class="project-action-btn" data-action="delete" title="Delete Project">🗑️</button>
                </div>
            </div>
            <div class="project-card__content">
                <h3 class="project-card__title">${project.name}</h3>
                <p class="project-card__description">${project.description || 'No description provided'}</p>
                <div class="project-card__meta">
                    <span class="project-card__documents">${project.documentCount || 0} documents</span>
                    <span class="project-card__date">${project.createdDate}</span>
                </div>
            </div>
        </div>
    `).join('');
}

function filterProjects() {
    filteredProjects = projects.filter(project => {
        const matchesFilter = currentFilter === 'All' || project.category === currentFilter;
        const matchesSearch = !currentSearch || 
            project.name.toLowerCase().includes(currentSearch.toLowerCase()) ||
            project.description.toLowerCase().includes(currentSearch.toLowerCase());
        
        return matchesFilter && matchesSearch;
    });
    
    renderProjects();
}

// Modal Management
function showCreateProjectModal() {
    if (createProjectModal) {
        createProjectModal.classList.remove('hidden');
    }
}

function hideCreateProjectModal() {
    if (createProjectModal) {
        createProjectModal.classList.add('hidden');
        if (createProjectForm) {
            createProjectForm.reset();
        }
    }
    clearSelectedFiles();
}

// File Selection
function clearSelectedFiles() {
    if (selectedFilesContainer) {
        selectedFilesContainer.innerHTML = '';
    }
}

function updateSelectedFiles() {
    if (!selectedFilesContainer || !projectFiles) return;
    
    const files = Array.from(projectFiles.files);
    if (files.length === 0) {
        selectedFilesContainer.innerHTML = '';
        return;
    }
    
    selectedFilesContainer.innerHTML = files.map((file, index) => `
        <div class="selected-file">
            <span class="file-name">${file.name}</span>
            <span class="file-size">(${formatFileSize(file.size)})</span>
            <button type="button" class="remove-file-btn" data-index="${index}">×</button>
        </div>
    `).join('');
}

function removeFileFromSelection(index) {
    if (!projectFiles) return;
    
    const dt = new DataTransfer();
    const files = Array.from(projectFiles.files);
    
    files.forEach((file, i) => {
        if (i !== index) dt.items.add(file);
    });
    
    projectFiles.files = dt.files;
    updateSelectedFiles();
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

// Chat Management
function showChatPage(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;

    currentProjectId = projectId;
    
    if (chatProjectTitle) chatProjectTitle.textContent = project.name;
    if (chatProjectSubtitle) chatProjectSubtitle.textContent = `Chat with your ${project.documentCount} documents`;
    
    // Reset chat
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="chat-message system-message">
                <div class="message-content">
                    <p>Initializing RAG system for "${project.name}"... Please wait.</p>
                </div>
            </div>
        `;
    }
    
    // Disable chat input until ready
    if (chatInput) {
        chatInput.disabled = true;
        chatInput.placeholder = "Initializing RAG system...";
    }

    // Show chat page
    if (homePage) homePage.classList.add('hidden');
    if (chatPage) chatPage.classList.remove('hidden');
    if (header) header.classList.add('header--collapsed');
    
    // Initialize RAG system
    initializeRAGSystem(projectId, project);
}

function showHomePage() {
    if (chatPage) chatPage.classList.add('hidden');
    if (homePage) homePage.classList.remove('hidden');
    if (header) header.classList.remove('header--collapsed');
    
    currentProjectId = null;
}

async function initializeRAGSystem(projectId, project) {
    try {
        const response = await fetch(`http://localhost:5001/api/initialize-project/${projectId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: project.name,
                filePaths: project.filePaths || []
            })
        });
        
        const result = await response.json();
        
        if (result.success) {
            updateSystemMessage(`✅ RAG system ready! I've processed ${result.file_count || 'your'} document(s). What would you like to know?`);
            
            if (chatInput) {
                chatInput.disabled = false;
                chatInput.placeholder = "Ask me anything about your documents...";
                chatInput.focus();
            }
        } else {
            updateSystemMessage(`❌ Failed to initialize RAG system: ${result.error}`);
        }
    } catch (error) {
        updateSystemMessage(`❌ Error connecting to RAG backend: ${error.message}`);
    }
}

function updateSystemMessage(message) {
    if (!chatMessages) return;
    
    const systemMsg = chatMessages.querySelector('.system-message .message-content p');
    if (systemMsg) {
        systemMsg.textContent = message;
    }
}

// Chat Input Management
function initChatInput() {
    if (!chatInput || !sendBtn) return;
    
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        
        const hasText = this.value.trim().length > 0;
        sendBtn.disabled = !hasText || this.disabled;
    });
    
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey && !this.disabled) {
            e.preventDefault();
            sendMessage();
        }
    });
}

function sendMessage() {
    const message = chatInput?.value?.trim();
    if (!message || !currentProjectId) return;
    
    // Add user message
    addMessage(message, 'user');
    
    // Clear input
    if (chatInput) {
        chatInput.value = '';
        chatInput.style.height = 'auto';
    }
    if (sendBtn) sendBtn.disabled = true;
    
    // Send to backend
    sendStreamingMessage(message);
}

async function sendStreamingMessage(message) {
    try {
        const response = await fetch(`http://localhost:5001/api/chat-stream/${currentProjectId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query: message })
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let assistantMessageId = addMessage('', 'assistant');
        
        while (true) {
            const { value, done } = await reader.read();
            if (done) break;
            
            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');
            
            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));
                        if (data.type === 'chunk') {
                            appendToMessage(assistantMessageId, data.content);
                        } else if (data.type === 'error') {
                            appendToMessage(assistantMessageId, `\n\n❌ Error: ${data.message}`);
                        }
                    } catch (e) {
                        console.log('Error parsing SSE data:', e);
                    }
                }
            }
        }
    } catch (error) {
        addMessage(`❌ Error: ${error.message}`, 'assistant');
    }
}

function addMessage(content, sender) {
    if (!chatMessages) return null;
    
    const messageId = `msg-${Date.now()}`;
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    messageDiv.id = messageId;
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${content}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    return messageId;
}

function appendToMessage(messageId, content) {
    const messageEl = document.getElementById(messageId);
    if (messageEl) {
        const p = messageEl.querySelector('p');
        if (p) {
            p.textContent += content;
            if (chatMessages) {
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        }
    }
}

function clearChat() {
    if (chatMessages) {
        chatMessages.innerHTML = `
            <div class="chat-message system-message">
                <div class="message-content">
                    <p>Chat cleared. What would you like to know?</p>
                </div>
            </div>
        `;
    }
    chatHistory = [];
}

function deleteProject(projectId) {
    const project = projects.find(p => p.id === projectId);
    if (!project) return;
    
    if (confirm(`Are you sure you want to delete "${project.name}"? This action cannot be undone.`)) {
        projects = projects.filter(p => p.id !== projectId);
        filterProjects();
        console.log(`Project "${project.name}" deleted`);
    }
}

// Event Listeners
function attachEventListeners() {
    // Theme toggle
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Filter buttons
    if (filterButtons) {
        filterButtons.addEventListener('click', (e) => {
            if (e.target.classList.contains('filter-btn')) {
                // Remove active class from all buttons
                filterButtons.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));
                
                // Add active class to clicked button
                e.target.classList.add('active');
                
                currentFilter = e.target.dataset.category;
                filterProjects();
            }
        });
    }

    // Search input
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            currentSearch = e.target.value;
            filterProjects();
        });
    }

    // Project grid clicks
    if (projectsGrid) {
        projectsGrid.addEventListener('click', (e) => {
            const card = e.target.closest('.project-card');
            const actionBtn = e.target.closest('.project-action-btn');
            
            if (actionBtn && card) {
                e.stopPropagation();
                const projectId = card.dataset.projectId;
                const action = actionBtn.dataset.action;
                
                if (action === 'chat') {
                    showChatPage(projectId);
                } else if (action === 'delete') {
                    deleteProject(projectId);
                }
            } else if (card) {
                const projectId = card.dataset.projectId;
                showChatPage(projectId);
            }
        });
    }

    // Create project button
    if (createProjectBtn) {
        createProjectBtn.addEventListener('click', showCreateProjectModal);
    }

    // Refresh projects button
    if (refreshProjectsBtn) {
        refreshProjectsBtn.addEventListener('click', () => {
            refreshProjectsBtn.disabled = true;
            refreshProjectsBtn.innerHTML = '<span class="btn__icon">⏳</span>Refreshing...';
            
            loadProjectsFromBackend();
            
            setTimeout(() => {
                refreshProjectsBtn.disabled = false;
                refreshProjectsBtn.innerHTML = '<span class="btn__icon">🔄</span>Refresh Projects';
            }, 1000);
        });
    }

    // Modal controls
    if (closeModal) closeModal.addEventListener('click', hideCreateProjectModal);
    if (cancelCreate) cancelCreate.addEventListener('click', hideCreateProjectModal);

    // File input
    if (projectFiles) {
        projectFiles.addEventListener('change', updateSelectedFiles);
    }

    // Selected files container
    if (selectedFilesContainer) {
        selectedFilesContainer.addEventListener('click', (e) => {
            if (e.target.classList.contains('remove-file-btn')) {
                const index = parseInt(e.target.dataset.index);
                removeFileFromSelection(index);
            }
        });
    }

    // Create project form
    if (createProjectForm) {
        createProjectForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const formData = new FormData(e.target);
            
            const files = Array.from(projectFiles?.files || []);
            const filePaths = files.map(file => file.name);
            
            const projectData = {
                name: formData.get('project-name') || document.getElementById('project-name')?.value,
                description: formData.get('project-description') || document.getElementById('project-description')?.value,
                category: formData.get('project-category') || document.getElementById('project-category')?.value,
                files: files,
                filePaths: filePaths
            };
            
            createNewProject(projectData);
        });
    }

    // Chat functionality
    if (sendBtn) sendBtn.addEventListener('click', sendMessage);
    if (clearChatBtn) clearChatBtn.addEventListener('click', clearChat);
    if (backButton) backButton.addEventListener('click', showHomePage);

    // Modal backdrop click
    if (createProjectModal) {
        createProjectModal.addEventListener('click', (e) => {
            if (e.target === createProjectModal) {
                hideCreateProjectModal();
            }
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            if (!createProjectModal?.classList.contains('hidden')) {
                hideCreateProjectModal();
            }
        }
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
