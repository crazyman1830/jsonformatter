/**
 * JSON Formatter Client-Side Application
 * This script is encapsulated in an App object to avoid polluting the global namespace.
 */

const App = {
    // Properties to hold DOM elements
    elements: {},
    // Timeout for debounced comment saving
    saveTimeout: null,

    /**
     * Initialize the application
     */
    init: function () {
        this.cacheDOMElements();
        this.setupTheme();
        this.addEventListeners();
        this.loadComments();
        setTimeout(() => this.alignLineNumbers(), 100);
    },

    /**
     * Cache all necessary DOM elements for performance
     */
    cacheDOMElements: function () {
        this.elements = {
            themeToggle: document.getElementById('theme-toggle'),
            jsonInput: document.getElementById('json-input'),
            jsonOutput: document.getElementById('json-output'),
            formatBtn: document.getElementById('format-btn'),
            copyBtn: document.getElementById('copy-btn'),
            copyWithCommentsBtn: document.getElementById('copy-with-comments-btn'),
            clearCommentsBtn: document.getElementById('clear-comments-btn'),
            errorMessage: document.getElementById('error-message'),
            lineNumbers: document.getElementById('line-numbers'),
            commentsTextarea: document.getElementById('comments-textarea'),
            commentsLineNumbers: document.getElementById('comments-line-numbers'),
            jsonHighlightOverlay: document.getElementById('json-highlight-overlay'),
        };
    },

    /**
     * Setup theme (Dark/Light)
     */
    setupTheme: function () {
        const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
        const currentTheme = localStorage.getItem('theme');

        if (currentTheme === 'dark' || (!currentTheme && prefersDarkScheme.matches)) {
            document.documentElement.setAttribute('data-theme', 'dark');
        }
    },

    /**
     * Add all event listeners
     */
    addEventListeners: function () {
        const {
            themeToggle, jsonInput, jsonOutput, formatBtn, copyBtn,
            copyWithCommentsBtn, clearCommentsBtn, commentsTextarea
        } = this.elements;

        // Theme toggle
        if (themeToggle) {
            themeToggle.addEventListener('click', () => {
                let theme = 'light';
                if (!document.documentElement.getAttribute('data-theme')) {
                    theme = 'dark';
                    document.documentElement.setAttribute('data-theme', 'dark');
                } else {
                    document.documentElement.removeAttribute('data-theme');
                }
                localStorage.setItem('theme', theme);
            });
        }

        formatBtn.addEventListener('click', () => this.formatJSON());
        copyBtn.addEventListener('click', () => this.copyToClipboard());
        copyWithCommentsBtn.addEventListener('click', () => this.copyWithComments());
        clearCommentsBtn.addEventListener('click', () => this.clearAllComments());

        commentsTextarea.addEventListener('input', () => {
            clearTimeout(this.saveTimeout);
            this.saveTimeout = setTimeout(() => this.saveComments(), 500);
            this.syncCommentsWithJSON();
        });

        commentsTextarea.addEventListener('click', () => this.handleCursorPosition());
        commentsTextarea.addEventListener('keyup', () => this.handleCursorPosition());
        commentsTextarea.addEventListener('focus', () => this.handleCursorPosition());

        jsonInput.addEventListener('input', () => {
            if (jsonOutput.value) {
                this.clearOutput();
                copyBtn.disabled = true;
                copyWithCommentsBtn.disabled = true;
                this.clearError();
            }
        });

        const syncScroll = (e) => {
            const { scrollTop } = e.target;
            this.elements.lineNumbers.scrollTop = scrollTop;
            this.elements.commentsTextarea.scrollTop = scrollTop;
            this.elements.commentsLineNumbers.scrollTop = scrollTop;
            this.elements.jsonHighlightOverlay.scrollTop = scrollTop;
            this.elements.jsonOutput.scrollTop = scrollTop;
        };

        jsonOutput.addEventListener('scroll', syncScroll);
        commentsTextarea.addEventListener('scroll', syncScroll);

        jsonInput.addEventListener('keydown', (e) => {
            if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.formatJSON();
            }
        });

        jsonInput.addEventListener('paste', () => {
            setTimeout(() => {
                const pastedText = jsonInput.value.trim();
                if (pastedText && this.isLikelyJSON(pastedText)) {
                    this.formatJSON();
                }
            }, 10);
        });

        window.addEventListener('beforeunload', (e) => {
            if (jsonInput.value.trim() && !jsonOutput.value.trim()) {
                e.preventDefault();
                e.returnValue = 'You have unformatted JSON. Are you sure you want to leave?';
                return e.returnValue;
            }
        });
    },

    /**
     * Format JSON by sending an AJAX request to the server
     */
    formatJSON: function () {
        const { jsonInput, formatBtn } = this.elements;
        const inputValue = jsonInput.value.trim();

        this.clearError();

        if (!inputValue) {
            this.showError('Please enter JSON data to format');
            return;
        }

        formatBtn.disabled = true;
        formatBtn.textContent = 'Formatting...';

        fetch('/api/format', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ json_data: inputValue })
        })
            .then(response => response.json().then(data => ({ status: response.status, data })))
            .then(result => this.handleFormatResponse(result.data, result.status))
            .catch(error => {
                console.error('Network error:', error);
                this.showError('Network error: Unable to connect to server');
            })
            .finally(() => {
                formatBtn.disabled = false;
                formatBtn.textContent = 'Format JSON';
            });
    },

    /**
     * Handle the response from the format endpoint
     */
    handleFormatResponse: function (data, status) {
        if (data.success && status === 200) {
            this.displayFormattedJSON(data.formatted_json);
            this.clearError();
            this.elements.copyBtn.disabled = false;
            this.elements.copyWithCommentsBtn.disabled = false;
        } else {
            this.showError(data.error_message || 'An error occurred while formatting JSON');
            this.clearOutput();
            this.elements.copyBtn.disabled = true;
            this.elements.copyWithCommentsBtn.disabled = true;
        }
    },

    /**
     * Display formatted JSON in the output area
     */
    displayFormattedJSON: function (formattedJSON) {
        this.elements.jsonOutput.value = formattedJSON;
        this.updateLineNumbers();
        this.updateCommentsLineNumbers();
        this.syncCommentsWithJSON();
        this.alignLineNumbers();
        this.elements.clearCommentsBtn.disabled = false;
    },

    /**
     * Align line numbers and textareas for consistent display
     */
    alignLineNumbers: function () {
        const { jsonOutput, lineNumbers, commentsLineNumbers, jsonHighlightOverlay, commentsTextarea } = this.elements;
        const computedStyle = window.getComputedStyle(jsonOutput);
        const lineHeight = computedStyle.lineHeight;
        const fontSize = computedStyle.fontSize;

        const elementsToStyle = [lineNumbers, commentsLineNumbers, jsonHighlightOverlay, commentsTextarea];
        elementsToStyle.forEach(el => {
            el.style.lineHeight = lineHeight;
            el.style.fontSize = fontSize;
        });
    },

    /**
     * Update line numbers for the main JSON output
     */
    updateLineNumbers: function () {
        const lines = this.elements.jsonOutput.value.split('\n');
        this.elements.lineNumbers.textContent = lines.map((_, i) => i + 1).join('\n');
    },

    /**
     * Update line numbers for the comments section
     */
    updateCommentsLineNumbers: function () {
        const jsonLines = this.elements.jsonOutput.value.split('\n');
        this.elements.commentsLineNumbers.textContent = jsonLines.map((_, i) => i + 1).join('\n');
    },

    /**
     * Sync comments textarea to have the same number of lines as the JSON output
     */
    syncCommentsWithJSON: function () {
        const { jsonOutput, commentsTextarea } = this.elements;
        if (!jsonOutput.value) return;

        const jsonLines = jsonOutput.value.split('\n');
        const commentLines = commentsTextarea.value.split('\n');

        if (commentLines.length < jsonLines.length) {
            const emptyLines = new Array(jsonLines.length - commentLines.length).fill('');
            commentsTextarea.value = commentLines.concat(emptyLines).join('\n');
        } else if (commentLines.length > jsonLines.length) {
            commentsTextarea.value = commentLines.slice(0, jsonLines.length).join('\n');
        }
    },

    /**
     * Highlight the corresponding JSON line based on cursor position in the comments textarea
     */
    handleCursorPosition: function () {
        const { jsonOutput, commentsTextarea } = this.elements;
        if (!jsonOutput.value) return;

        const cursorPosition = commentsTextarea.selectionStart;
        const textBeforeCursor = commentsTextarea.value.substring(0, cursorPosition);
        const currentLine = textBeforeCursor.split('\n').length;
        this.highlightJSONLine(currentLine);
    },

    /**
     * Highlight a specific line in the JSON output
     */
    highlightJSONLine: function (lineNumber) {
        const { jsonHighlightOverlay, jsonOutput } = this.elements;
        const lines = jsonOutput.value.split('\n');

        if (lineNumber > lines.length) return;

        // Create a temporary element to measure line height accurately
        // or assume it matches the computed style since we aligned them

        // Simple text-based overlay approach
        // We will fill the overlay with newlines and put a span on the target line

        let overlayContent = '';
        for (let i = 1; i < lines.length + 1; i++) {
            if (i === lineNumber) {
                overlayContent += `<div class="highlighted-line">&nbsp;</div>\n`;
            } else {
                overlayContent += '\n';
            }
        }

        // Note: This simple overlay might desync if wrapping occurs, but we have disabled wrapping for now
        // For a more robust solution, we'd need to replicate the text content exactly

        // Better approach for now: just clear it, we are using a simple line-based highlighter
        // The CSS class .highlighted-line handles the visual

        // Actually, to make the highlight visible behind the text, we need to replicate the structure
        // But since we are using a monospace font and no wrapping (resize: none, overflow: auto),
        // we can just use newlines.

        // Let's refine the overlay content to match the text content structure roughly
        // or just use absolute positioning for the highlight bar if we knew the line height in pixels.

        // Current implementation in style.css expects .highlighted-line to be an inline element
        // Let's try to just set the innerHTML.

        const content = lines.map((line, index) => {
            if (index + 1 === lineNumber) {
                return `<span class="highlighted-line">${line || ' '}</span>`;
            }
            return line; // Just the text, but we need to preserve height
        }).join('\n');

        // This replaces the text in the overlay. The overlay text color is transparent,
        // but the background of the span will show.
        jsonHighlightOverlay.innerHTML = content;
    },

    /**
     * Copy formatted JSON to clipboard
     */
    copyToClipboard: function () {
        const { jsonOutput } = this.elements;
        if (!jsonOutput.value) return;

        navigator.clipboard.writeText(jsonOutput.value).then(() => {
            this.showSuccess('JSON copied to clipboard!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showError('Failed to copy to clipboard');
        });
    },

    /**
     * Copy JSON with comments to clipboard
     */
    copyWithComments: function () {
        const { jsonOutput, commentsTextarea } = this.elements;
        if (!jsonOutput.value) return;

        const jsonLines = jsonOutput.value.split('\n');
        const commentLines = commentsTextarea.value.split('\n');

        const combined = jsonLines.map((line, index) => {
            const comment = commentLines[index] ? ` // ${commentLines[index]}` : '';
            return line + comment;
        }).join('\n');

        navigator.clipboard.writeText(combined).then(() => {
            this.showSuccess('JSON with comments copied!');
        }).catch(err => {
            console.error('Failed to copy:', err);
            this.showError('Failed to copy to clipboard');
        });
    },

    /**
     * Clear all comments
     */
    clearAllComments: function () {
        if (confirm('Are you sure you want to clear all comments?')) {
            this.elements.commentsTextarea.value = '';
            this.syncCommentsWithJSON();
            this.saveComments();
        }
    },

    /**
     * Save comments to local storage (mock implementation for now)
     * In a real app, this might send to the server
     */
    saveComments: function () {
        // Placeholder for saving logic
        // console.log('Comments saved');
    },

    /**
     * Load comments (mock implementation)
     */
    loadComments: function () {
        // Placeholder for loading logic
    },

    /**
     * Clear output and reset state
     */
    clearOutput: function () {
        this.elements.jsonOutput.value = '';
        this.elements.lineNumbers.textContent = '';
        this.elements.commentsLineNumbers.textContent = '';
        this.elements.jsonHighlightOverlay.innerHTML = '';
        // We don't clear comments textarea here to preserve them if user is just editing JSON slightly
        // But we might want to warn if they desync too much.
    },

    /**
     * Show error message
     */
    showError: function (message) {
        const { errorMessage } = this.elements;
        errorMessage.textContent = message;
        errorMessage.classList.add('show');
        setTimeout(() => {
            errorMessage.classList.remove('show');
        }, 5000);
    },

    /**
     * Clear error message
     */
    clearError: function () {
        const { errorMessage } = this.elements;
        errorMessage.textContent = '';
        errorMessage.classList.remove('show');
    },

    /**
     * Show success message (toast)
     */
    showSuccess: function (message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success-message';
        successDiv.textContent = message;
        document.body.appendChild(successDiv);

        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    },

    /**
     * Simple check if string looks like JSON
     */
    isLikelyJSON: function (text) {
        const trimmed = text.trim();
        return (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
            (trimmed.startsWith('[') && trimmed.endsWith(']'));
    }
};

// Initialize app when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    App.init();
});
