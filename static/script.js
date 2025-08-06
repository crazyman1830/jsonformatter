/**
 * JSON Formatter Client-Side JavaScript
 * Handles format button functionality and AJAX requests
 */

document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const jsonInput = document.getElementById('json-input');
    const jsonOutput = document.getElementById('json-output');
    const formatBtn = document.getElementById('format-btn');
    const copyBtn = document.getElementById('copy-btn');
    const copyWithCommentsBtn = document.getElementById('copy-with-comments-btn');
    const clearCommentsBtn = document.getElementById('clear-comments-btn');
    const errorMessage = document.getElementById('error-message');
    const lineNumbers = document.getElementById('line-numbers');
    const commentsTextarea = document.getElementById('comments-textarea');
    const commentsLineNumbers = document.getElementById('comments-line-numbers');
    const jsonHighlightOverlay = document.getElementById('json-highlight-overlay');

    // Add event listeners
    formatBtn.addEventListener('click', formatJSON);
    copyBtn.addEventListener('click', copyToClipboard);
    copyWithCommentsBtn.addEventListener('click', copyWithComments);
    clearCommentsBtn.addEventListener('click', clearAllComments);

    // Auto-save comments with debounce
    commentsTextarea.addEventListener('input', function() {
        clearTimeout(this.saveTimeout);
        this.saveTimeout = setTimeout(saveComments, 500);
        syncCommentsWithJSON();
    });

    // Add cursor position tracking for line highlighting
    commentsTextarea.addEventListener('click', handleCursorPosition);
    commentsTextarea.addEventListener('keyup', handleCursorPosition);
    commentsTextarea.addEventListener('focus', handleCursorPosition);

    /**
     * Format JSON by sending AJAX request to the server
     */
    function formatJSON() {
        // Get input value
        const inputValue = jsonInput.value.trim();

        // Clear previous error messages
        clearError();

        // Validate input is not empty
        if (!inputValue) {
            showError('Please enter JSON data to format');
            return;
        }

        // Disable format button during processing
        formatBtn.disabled = true;
        formatBtn.textContent = 'Formatting...';

        // Prepare request data
        const requestData = {
            json_data: inputValue
        };

        // Send AJAX request to format endpoint
        fetch('/format', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            return response.json().then(data => ({
                status: response.status,
                data: data
            }));
        })
        .then(result => {
            handleFormatResponse(result.data, result.status);
        })
        .catch(error => {
            console.error('Network error:', error);
            showError('Network error: Unable to connect to server');
        })
        .finally(() => {
            // Re-enable format button
            formatBtn.disabled = false;
            formatBtn.textContent = 'Format JSON';
        });
    }

    /**
     * Handle the response from the format endpoint
     * @param {Object} data - Response data from server
     * @param {number} status - HTTP status code
     */
    function handleFormatResponse(data, status) {
        if (data.success && status === 200) {
            // Successful formatting
            displayFormattedJSON(data.formatted_json);
            clearError();
            // Enable copy buttons
            copyBtn.disabled = false;
            copyWithCommentsBtn.disabled = false;
        } else {
            // Error occurred
            showError(data.error_message || 'An error occurred while formatting JSON');
            clearOutput();
            // Disable copy buttons
            copyBtn.disabled = true;
            copyWithCommentsBtn.disabled = true;
        }
    }

    /**
     * Display formatted JSON in the output area
     * @param {string} formattedJSON - The formatted JSON string
     */
    function displayFormattedJSON(formattedJSON) {
        jsonOutput.value = formattedJSON;
        updateLineNumbers();
        updateCommentsLineNumbers();
        syncCommentsWithJSON();
        alignLineNumbers();
        clearCommentsBtn.disabled = false;
    }

    /**
     * Align line numbers with textarea content
     */
    function alignLineNumbers() {
        // Get computed styles
        const jsonStyle = window.getComputedStyle(jsonOutput);
        const lineHeight = jsonStyle.lineHeight;
        const fontSize = jsonStyle.fontSize;

        // Apply same line height to line numbers
        lineNumbers.style.lineHeight = lineHeight;
        lineNumbers.style.fontSize = fontSize;
        commentsLineNumbers.style.lineHeight = lineHeight;
        commentsLineNumbers.style.fontSize = fontSize;
        jsonHighlightOverlay.style.lineHeight = lineHeight;
        jsonHighlightOverlay.style.fontSize = fontSize;

        // Ensure comments textarea matches
        commentsTextarea.style.lineHeight = lineHeight;
        commentsTextarea.style.fontSize = fontSize;
    }

    /**
     * Update line numbers display for JSON output
     */
    function updateLineNumbers() {
        const lines = jsonOutput.value.split('\n');
        const lineNumbersText = lines.map((_, index) => (index + 1).toString()).join('\n');
        lineNumbers.textContent = lineNumbersText;
    }

    /**
     * Update line numbers display for comments
     */
    function updateCommentsLineNumbers() {
        const jsonLines = jsonOutput.value.split('\n');
        const lineNumbersText = jsonLines.map((_, index) => (index + 1).toString()).join('\n');
        commentsLineNumbers.textContent = lineNumbersText;
    }

    /**
     * Sync comments textarea with JSON line count
     */
    function syncCommentsWithJSON() {
        if (!jsonOutput.value) return;

        const jsonLines = jsonOutput.value.split('\n');
        const commentLines = commentsTextarea.value.split('\n');

        // Adjust comments to match JSON line count
        if (commentLines.length < jsonLines.length) {
            // Add empty lines to match JSON
            const emptyLines = new Array(jsonLines.length - commentLines.length).fill('');
            commentsTextarea.value = commentLines.concat(emptyLines).join('\n');
        } else if (commentLines.length > jsonLines.length) {
            // Trim extra lines
            commentsTextarea.value = commentLines.slice(0, jsonLines.length).join('\n');
        }
    }

    /**
     * Handle cursor position changes in comments textarea
     */
    function handleCursorPosition() {
        if (!jsonOutput.value) return;

        const cursorPosition = commentsTextarea.selectionStart;
        const textBeforeCursor = commentsTextarea.value.substring(0, cursorPosition);
        const currentLine = textBeforeCursor.split('\n').length;

        highlightJSONLine(currentLine);
    }

    /**
     * Highlight a specific line in the JSON output
     * @param {number} lineNumber - Line number to highlight (1-based)
     */
    function highlightJSONLine(lineNumber) {
        if (!jsonOutput.value || lineNumber < 1) {
            jsonHighlightOverlay.innerHTML = '';
            return;
        }

        const jsonLines = jsonOutput.value.split('\n');
        if (lineNumber > jsonLines.length) {
            jsonHighlightOverlay.innerHTML = '';
            return;
        }

        // Create highlight overlay content
        let overlayContent = '';
        jsonLines.forEach((line, index) => {
            if (index + 1 === lineNumber) {
                overlayContent += `<span class="highlighted-line">${line}</span>\n`;
            } else {
                overlayContent += line + '\n';
            }
        });

        // Remove last newline
        overlayContent = overlayContent.slice(0, -1);
        jsonHighlightOverlay.innerHTML = overlayContent;

        // Auto-clear highlight after 3 seconds
        clearTimeout(window.highlightTimeout);
        window.highlightTimeout = setTimeout(() => {
            jsonHighlightOverlay.innerHTML = '';
        }, 3000);
    }

    /**
     * Clear all comments
     */
    function clearAllComments() {
        commentsTextarea.value = '';
        saveComments();
    }

    /**
     * Save comments to server
     */
    function saveComments() {
        fetch('/comments', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                comments: commentsTextarea.value
            })
        })
        .catch(error => {
            console.error('Error saving comments:', error);
        });
    }

    /**
     * Load comments from server
     */
    function loadComments() {
        fetch('/comments')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                commentsTextarea.value = data.comments || '';
            }
        })
        .catch(error => {
            console.error('Error loading comments:', error);
        });
    }

    /**
     * Copy JSON with comments to clipboard
     */
    function copyWithComments() {
        if (!jsonOutput.value.trim()) {
            showError('No formatted JSON to copy');
            return;
        }

        const jsonLines = jsonOutput.value.split('\n');
        const commentLines = commentsTextarea.value.split('\n');
        let result = '';

        jsonLines.forEach((line, index) => {
            const comment = commentLines[index];

            if (comment && comment.trim()) {
                result += line + ' // ' + comment.trim() + '\n';
            } else {
                result += line + '\n';
            }
        });

        // Remove last newline
        result = result.slice(0, -1);

        try {
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(result)
                    .then(() => {
                        showCopySuccess(copyWithCommentsBtn, 'Copied with Comments!');
                    })
                    .catch(err => {
                        console.error('Clipboard API failed:', err);
                        fallbackCopyText(result, copyWithCommentsBtn, 'Copied with Comments!');
                    });
            } else {
                fallbackCopyText(result, copyWithCommentsBtn, 'Copied with Comments!');
            }
        } catch (err) {
            console.error('Copy failed:', err);
            showError('Failed to copy to clipboard');
        }
    }

    /**
     * Fallback copy method for custom text
     */
    function fallbackCopyText(text, button, successText) {
        const tempTextArea = document.createElement('textarea');
        tempTextArea.value = text;
        document.body.appendChild(tempTextArea);
        tempTextArea.select();

        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showCopySuccess(button, successText);
            } else {
                showError('Failed to copy to clipboard');
            }
        } catch (err) {
            console.error('execCommand copy failed:', err);
            showError('Copy to clipboard not supported in this browser');
        } finally {
            document.body.removeChild(tempTextArea);
        }
    }

    /**
     * Show error message
     * @param {string} message - Error message to display
     */
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    /**
     * Clear error message
     */
    function clearError() {
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
    }

    /**
     * Clear output area
     */
    function clearOutput() {
        jsonOutput.value = '';
        lineNumbers.textContent = '';
        commentsLineNumbers.textContent = '';
        jsonHighlightOverlay.innerHTML = '';
        clearCommentsBtn.disabled = true;
        copyWithCommentsBtn.disabled = true;
    }

    /**
     * Copy formatted JSON to clipboard with visual feedback
     */
    function copyToClipboard() {
        // Check if there's content to copy
        if (!jsonOutput.value.trim()) {
            showError('No formatted JSON to copy');
            return;
        }

        // Try to copy to clipboard
        try {
            // Select the output text
            jsonOutput.select();
            jsonOutput.setSelectionRange(0, 99999); // For mobile devices

            // Use the modern clipboard API if available
            if (navigator.clipboard && window.isSecureContext) {
                navigator.clipboard.writeText(jsonOutput.value)
                    .then(() => {
                        showCopySuccess();
                    })
                    .catch(err => {
                        console.error('Clipboard API failed:', err);
                        // Fallback to execCommand
                        fallbackCopy();
                    });
            } else {
                // Fallback for older browsers
                fallbackCopy();
            }
        } catch (err) {
            console.error('Copy failed:', err);
            showError('Failed to copy to clipboard');
        }
    }

    /**
     * Fallback copy method using execCommand
     */
    function fallbackCopy() {
        try {
            const successful = document.execCommand('copy');
            if (successful) {
                showCopySuccess();
            } else {
                showError('Failed to copy to clipboard');
            }
        } catch (err) {
            console.error('execCommand copy failed:', err);
            showError('Copy to clipboard not supported in this browser');
        }
    }

    /**
     * Show copy success feedback
     */
    function showCopySuccess(button = copyBtn, successText = 'Copied!') {
        // Store original button text
        const originalText = button.textContent;

        // Show success feedback
        button.textContent = successText;
        button.style.backgroundColor = '#28a745';

        // Clear any existing error messages
        clearError();

        // Reset button after 2 seconds
        setTimeout(() => {
            button.textContent = originalText;
            button.style.backgroundColor = '';
        }, 2000);
    }

    /**
     * Enhanced error handling for different error types
     * @param {string} message - Error message to display
     */
    function showError(message) {
        // Enhanced error message display
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';

        // Add error styling
        errorMessage.className = 'error-message show';

        // Auto-hide error after 5 seconds for non-critical errors
        if (!message.toLowerCase().includes('invalid json')) {
            setTimeout(() => {
                clearError();
            }, 5000);
        }
    }

    /**
     * Enhanced clear error with animation
     */
    function clearError() {
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        errorMessage.className = 'error-message';
    }

    /**
     * Handle edge cases and user interactions
     */

    // Clear output and disable copy button when input changes
    jsonInput.addEventListener('input', function() {
        if (jsonOutput.value) {
            clearOutput();
            copyBtn.disabled = true;
            copyWithCommentsBtn.disabled = true;
            clearError();
        }
    });

    // Sync scroll between JSON output, line numbers, and comments
    jsonOutput.addEventListener('scroll', function() {
        lineNumbers.scrollTop = this.scrollTop;
        commentsTextarea.scrollTop = this.scrollTop;
        commentsLineNumbers.scrollTop = this.scrollTop;
        jsonHighlightOverlay.scrollTop = this.scrollTop;
    });

    commentsTextarea.addEventListener('scroll', function() {
        lineNumbers.scrollTop = this.scrollTop;
        jsonOutput.scrollTop = this.scrollTop;
        commentsLineNumbers.scrollTop = this.scrollTop;
        jsonHighlightOverlay.scrollTop = this.scrollTop;
    });

    // Load comments on page load
    loadComments();

    // Initialize alignment on page load
    setTimeout(alignLineNumbers, 100);

    // Handle Enter key in input (Ctrl+Enter to format)
    jsonInput.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();
            formatJSON();
        }
    });

    // Handle paste events - auto-format if valid JSON
    jsonInput.addEventListener('paste', function(event) {
        // Small delay to allow paste to complete
        setTimeout(() => {
            const pastedText = jsonInput.value.trim();
            if (pastedText && isLikelyJSON(pastedText)) {
                // Auto-format if it looks like JSON
                setTimeout(formatJSON, 100);
            }
        }, 10);
    });

    /**
     * Simple heuristic to check if text looks like JSON
     * @param {string} text - Text to check
     * @returns {boolean} - True if text looks like JSON
     */
    function isLikelyJSON(text) {
        const trimmed = text.trim();
        return (trimmed.startsWith('{') && trimmed.endsWith('}')) ||
               (trimmed.startsWith('[') && trimmed.endsWith(']'));
    }

    // Handle window beforeunload to warn about unsaved changes
    window.addEventListener('beforeunload', function(event) {
        if (jsonInput.value.trim() && !jsonOutput.value.trim()) {
            event.preventDefault();
            event.returnValue = 'You have unformatted JSON. Are you sure you want to leave?';
            return event.returnValue;
        }
    });
});
