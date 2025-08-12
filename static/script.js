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
    init: function() {
        this.cacheDOMElements();
        this.addEventListeners();
        this.loadComments();
        setTimeout(() => this.alignLineNumbers(), 100);
    },

    /**
     * Cache all necessary DOM elements for performance
     */
    cacheDOMElements: function() {
        this.elements = {
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
     * Add all event listeners
     */
    addEventListeners: function() {
        const { jsonInput, jsonOutput, formatBtn, copyBtn, copyWithCommentsBtn, clearCommentsBtn, commentsTextarea } = this.elements;

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
    formatJSON: function() {
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
    handleFormatResponse: function(data, status) {
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
    displayFormattedJSON: function(formattedJSON) {
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
    alignLineNumbers: function() {
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
    updateLineNumbers: function() {
        const lines = this.elements.jsonOutput.value.split('\n');
        this.elements.lineNumbers.textContent = lines.map((_, i) => i + 1).join('\n');
    },

    /**
     * Update line numbers for the comments section
     */
    updateCommentsLineNumbers: function() {
        const jsonLines = this.elements.jsonOutput.value.split('\n');
        this.elements.commentsLineNumbers.textContent = jsonLines.map((_, i) => i + 1).join('\n');
    },

    /**
     * Sync comments textarea to have the same number of lines as the JSON output
     */
    syncCommentsWithJSON: function() {
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
    handleCursorPosition: function() {
        const { jsonOutput, commentsTextarea } = this.elements;
        if (!jsonOutput.value) return;

        const cursorPosition = commentsTextarea.selectionStart;
        const textBeforeCursor = commentsTextarea.value.substring(0, cursorPosition);
        const currentLine = textBeforeCursor.split('\n').length;
        this.highlightJSONLine(currentLine);
    },

    /**
     * Apply a highlight to a specific line in the JSON output
     */
    highlightJSONLine: function(lineNumber) {
        const { jsonOutput, jsonHighlightOverlay } = this.elements;
        if (!jsonOutput.value || lineNumber < 1) {
            jsonHighlightOverlay.innerHTML = '';
            return;
        }

        const jsonLines = jsonOutput.value.split('\n');
        if (lineNumber > jsonLines.length) {
            jsonHighlightOverlay.innerHTML = '';
            return;
        }

        const overlayContent = jsonLines.map((line, index) =>
            (index + 1 === lineNumber) ? `<span class="highlighted-line">${line || ' '}</span>` : (line || ' ')
        ).join('\n');

        jsonHighlightOverlay.innerHTML = overlayContent;

        clearTimeout(this.highlightTimeout);
        this.highlightTimeout = setTimeout(() => {
            jsonHighlightOverlay.innerHTML = '';
        }, 3000);
    },

    /**
     * Clear all comments and save the change
     */
    clearAllComments: function() {
        this.elements.commentsTextarea.value = '';
        this.saveComments();
    },

    /**
     * Save comments to the server
     */
    saveComments: function() {
        fetch('/api/comments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ comments: this.elements.commentsTextarea.value })
        }).catch(error => console.error('Error saving comments:', error));
    },

    /**
     * Load comments from the server
     */
    loadComments: function() {
        fetch('/api/comments')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    this.elements.commentsTextarea.value = data.comments || '';
                }
            })
            .catch(error => console.error('Error loading comments:', error));
    },

    /**
     * Copy JSON to clipboard
     */
    copyToClipboard: function() {
        const textToCopy = this.elements.jsonOutput.value;
        if (!textToCopy.trim()) {
            this.showError('No formatted JSON to copy');
            return;
        }
        this._copyText(textToCopy, this.elements.copyBtn, 'Copied!');
    },

    /**
     * Copy JSON with comments to clipboard
     */
    copyWithComments: function() {
        const { jsonOutput, commentsTextarea } = this.elements;
        if (!jsonOutput.value.trim()) {
            this.showError('No formatted JSON to copy');
            return;
        }

        const jsonLines = jsonOutput.value.split('\n');
        const commentLines = commentsTextarea.value.split('\n');

        const result = jsonLines.map((line, index) => {
            const comment = commentLines[index];
            return (comment && comment.trim()) ? `${line} // ${comment.trim()}` : line;
        }).join('\n');

        this._copyText(result, this.elements.copyWithCommentsBtn, 'Copied with Comments!');
    },

    /**
     * Private helper to copy text to the clipboard, with fallback
     */
    _copyText: function(text, button, successText) {
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(text)
                .then(() => this.showCopySuccess(button, successText))
                .catch(err => {
                    console.error('Clipboard API failed:', err);
                    this._fallbackCopy(text, button, successText);
                });
        } else {
            this._fallbackCopy(text, button, successText);
        }
    },

    /**
     * Fallback copy method using a temporary textarea
     */
    _fallbackCopy: function(text, button, successText) {
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                this.showCopySuccess(button, successText);
            } else {
                this.showError('Failed to copy to clipboard');
            }
        } catch (err) {
            console.error('execCommand copy failed:', err);
            this.showError('Copy to clipboard not supported in this browser');
        }
        document.body.removeChild(textArea);
    },

    /**
     * Show a temporary success message on a button
     */
    showCopySuccess: function(button, successText) {
        const originalText = button.textContent;
        button.textContent = successText;
        button.style.backgroundColor = '#28a745';
        this.clearError();

        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    },

    /**
     * Display an error message
     */
    showError: function(message) {
        const { errorMessage } = this.elements;
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.className = 'error-message show';

        setTimeout(() => {
            if (errorMessage.textContent === message) {
                this.clearError();
            }
        }, 5000);
    },

    /**
     * Clear the error message
     */
    clearError: function() {
        const { errorMessage } = this.elements;
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        errorMessage.className = 'error-message';
    },

    /**
     * Clear all output areas
     */
    clearOutput: function() {
        const { jsonOutput, lineNumbers, commentsLineNumbers, jsonHighlightOverlay, clearCommentsBtn, copyWithCommentsBtn } = this.elements;
        jsonOutput.value = '';
        lineNumbers.textContent = '';
        commentsLineNumbers.textContent = '';
        jsonHighlightOverlay.innerHTML = '';
        clearCommentsBtn.disabled = true;
        copyWithCommentsBtn.disabled = true;
    },

    /**
     * Heuristic to check if a string is likely to be JSON
     */
    isLikelyJSON: function(text) {
        const trimmed = text.trim();
        return (trimmed.startsWith('{') && trimmed.endsWith('}')) || (trimmed.startsWith('[') && trimmed.endsWith(']'));
    }
};

// Initialize the App when the DOM is ready
document.addEventListener('DOMContentLoaded', () => App.init());
>>>>>>> REPLACE
