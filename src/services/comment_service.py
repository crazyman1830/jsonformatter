"""
Comment management service with pluggable storage backends.

This service provides a clean interface for managing user comments with
support for different storage backends through abstract interfaces.
"""

import logging
from typing import List, Optional, Dict, Any
from abc import ABC, abstractmethod

from core.exceptions import ValidationError, ProcessingError


class CommentStorage(ABC):
    """
    Abstract interface for comment storage backends.

    This interface defines the contract for comment storage implementations,
    allowing for different storage strategies (session, database, file, etc.).
    """

    @abstractmethod
    def save_comments(self, session_id: str, comments: List[str]) -> bool:
        """
        Save comments for a given session.

        Args:
            session_id: Unique identifier for the session
            comments: List of comment strings to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        pass

    @abstractmethod
    def load_comments(self, session_id: str) -> List[str]:
        """
        Load comments for a given session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            List[str]: List of comment strings, empty list if none found
        """
        pass

    @abstractmethod
    def clear_comments(self, session_id: str) -> bool:
        """
        Clear all comments for a given session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if clear was successful, False otherwise
        """
        pass

    @abstractmethod
    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session has any stored comments.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if session has comments, False otherwise
        """
        pass


class SessionCommentStorage(CommentStorage):
    """
    Session-based comment storage implementation.

    This implementation stores comments in memory using a dictionary
    keyed by session ID. Comments are lost when the application restarts.
    """

    def __init__(self) -> None:
        """Initialize the session storage."""
        self._storage: Dict[str, List[str]] = {}
        self._logger = logging.getLogger(__name__)
        self._logger.debug("SessionCommentStorage initialized")

    def save_comments(self, session_id: str, comments: Any) -> bool:
        """
        Save comments for a session in memory.

        Args:
            session_id: Unique identifier for the session
            comments: List of comment strings to save

        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            if not session_id:
                self._logger.error("Session ID cannot be empty")
                return False

            if not isinstance(comments, list):
                self._logger.error("Comments must be a list")
                return False

            # Filter out None values and convert to strings
            clean_comments = [
                str(comment) if comment is not None else "" for comment in comments
            ]

            self._storage[session_id] = clean_comments
            self._logger.debug(
                f"Saved {len(clean_comments)} comments for session {session_id}"
            )
            return True

        except Exception as e:
            self._logger.error(
                f"Failed to save comments for session {session_id}: {str(e)}"
            )
            return False

    def load_comments(self, session_id: str) -> List[str]:
        """
        Load comments for a session from memory.

        Args:
            session_id: Unique identifier for the session

        Returns:
            List[str]: List of comment strings, empty list if none found
        """
        try:
            if not session_id:
                self._logger.warning("Session ID cannot be empty")
                return []

            comments = self._storage.get(session_id, [])
            self._logger.debug(
                f"Loaded {len(comments)} comments for session {session_id}"
            )
            return comments

        except Exception as e:
            self._logger.error(
                f"Failed to load comments for session {session_id}: {str(e)}"
            )
            return []

    def clear_comments(self, session_id: str) -> bool:
        """
        Clear all comments for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if clear was successful, False otherwise
        """
        try:
            if not session_id:
                self._logger.error("Session ID cannot be empty")
                return False

            if session_id in self._storage:
                del self._storage[session_id]
                self._logger.debug(f"Cleared comments for session {session_id}")
            else:
                self._logger.debug(
                    f"No comments found to clear for session {session_id}"
                )

            return True

        except Exception as e:
            self._logger.error(
                f"Failed to clear comments for session {session_id}: {str(e)}"
            )
            return False

    def session_exists(self, session_id: str) -> bool:
        """
        Check if a session has any stored comments.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if session has comments, False otherwise
        """
        try:
            if not session_id:
                return False

            exists = session_id in self._storage and len(self._storage[session_id]) > 0
            self._logger.debug(f"Session {session_id} exists: {exists}")
            return exists

        except Exception as e:
            self._logger.error(
                f"Failed to check session existence for {session_id}: {str(e)}"
            )
            return False

    def get_session_count(self) -> int:
        """
        Get the number of active sessions with comments.

        Returns:
            int: Number of sessions with stored comments
        """
        return len(self._storage)

    def get_all_session_ids(self) -> List[str]:
        """
        Get all session IDs that have stored comments.

        Returns:
            List[str]: List of session IDs
        """
        return list(self._storage.keys())


class CommentService:
    """
    Service for managing user comments with pluggable storage backends.

    This service provides a high-level interface for comment operations
    while delegating storage concerns to pluggable backend implementations.
    """

    def __init__(
        self, storage: CommentStorage, logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Initialize the comment service.

        Args:
            storage: Storage backend implementation
            logger: Optional logger instance for dependency injection
        """
        self.storage = storage
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("CommentService initialized")

    def save_comments(self, session_id: str, comments_text: Any) -> bool:
        """
        Save comments from a text string, splitting by lines.

        Args:
            session_id: Unique identifier for the session
            comments_text: Multi-line string containing comments

        Returns:
            bool: True if save was successful, False otherwise

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If save operation fails
        """
        self.logger.debug(f"Saving comments for session {session_id}")

        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        if comments_text is None:
            error_msg = "Comments text cannot be None"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            # Split comments by lines and clean up
            if comments_text.strip():
                comments_list = [line.strip() for line in comments_text.splitlines()]
                # Remove empty lines
                comments_list = [comment for comment in comments_list if comment]
            else:
                comments_list = []

            success = self.storage.save_comments(session_id, comments_list)

            if success:
                self.logger.info(
                    f"Successfully saved {len(comments_list)} comments for session {session_id}"
                )
            else:
                self.logger.warning(f"Failed to save comments for session {session_id}")
                raise ProcessingError("Failed to save comments to storage")

            return success

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error saving comments: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def load_comments(self, session_id: str) -> str:
        """
        Load comments for a session and return as a multi-line string.

        Args:
            session_id: Unique identifier for the session

        Returns:
            str: Multi-line string containing comments, empty string if none found

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If load operation fails
        """
        self.logger.debug(f"Loading comments for session {session_id}")

        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            comments_list = self.storage.load_comments(session_id)
            comments_text = "\n".join(comments_list)

            self.logger.debug(
                f"Loaded {len(comments_list)} comments for session {session_id}"
            )
            return comments_text

        except Exception as e:
            error_msg = f"Unexpected error loading comments: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def clear_comments(self, session_id: str) -> bool:
        """
        Clear all comments for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if clear was successful, False otherwise

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If clear operation fails
        """
        self.logger.debug(f"Clearing comments for session {session_id}")

        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            success = self.storage.clear_comments(session_id)

            if success:
                self.logger.info(
                    f"Successfully cleared comments for session {session_id}"
                )
            else:
                self.logger.warning(
                    f"Failed to clear comments for session {session_id}"
                )
                raise ProcessingError("Failed to clear comments from storage")

            return success

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error clearing comments: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def has_comments(self, session_id: str) -> bool:
        """
        Check if a session has any stored comments.

        Args:
            session_id: Unique identifier for the session

        Returns:
            bool: True if session has comments, False otherwise

        Raises:
            ValidationError: If input validation fails
        """
        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            return self.storage.session_exists(session_id)
        except Exception as e:
            self.logger.error(f"Error checking comments existence: {str(e)}")
            return False

    def get_comment_count(self, session_id: str) -> int:
        """
        Get the number of comments for a session.

        Args:
            session_id: Unique identifier for the session

        Returns:
            int: Number of comments, 0 if none found

        Raises:
            ValidationError: If input validation fails
        """
        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            comments_list = self.storage.load_comments(session_id)
            return len(comments_list)
        except Exception as e:
            self.logger.error(f"Error getting comment count: {str(e)}")
            return 0

    def synchronize_with_json_lines(
        self, session_id: str, json_line_count: int
    ) -> bool:
        """
        Synchronize comments with JSON line count, padding or truncating as needed.

        Args:
            session_id: Unique identifier for the session
            json_line_count: Number of lines in the formatted JSON

        Returns:
            bool: True if synchronization was successful, False otherwise

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If synchronization fails
        """
        self.logger.debug(
            f"Synchronizing comments for session {session_id} with {json_line_count} JSON lines"
        )

        # Input validation
        if not session_id or not session_id.strip():
            error_msg = "Session ID cannot be empty"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        if json_line_count < 0:
            error_msg = "JSON line count cannot be negative"
            self.logger.error(error_msg)
            raise ValidationError(error_msg)

        try:
            current_comments = self.storage.load_comments(session_id)
            current_count = len(current_comments)

            if current_count == json_line_count:
                # Already synchronized
                self.logger.debug(
                    f"Comments already synchronized for session {session_id}"
                )
                return True
            elif current_count < json_line_count:
                # Pad with empty comments
                padded_comments = current_comments + [""] * (
                    json_line_count - current_count
                )
                success = self.storage.save_comments(session_id, padded_comments)
                self.logger.info(
                    f"Padded comments from {current_count} to {json_line_count} "
                    f"for session {session_id}"
                )
            else:
                # Truncate comments
                truncated_comments = current_comments[:json_line_count]
                success = self.storage.save_comments(session_id, truncated_comments)
                self.logger.info(
                    f"Truncated comments from {current_count} to {json_line_count} "
                    f"for session {session_id}"
                )

            if not success:
                raise ProcessingError("Failed to save synchronized comments")

            return success

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error synchronizing comments: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e
