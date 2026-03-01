"""
SSH Sync Module
Handles syncing markdown files to remote server via SSH/SFTP
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

import paramiko

logger = logging.getLogger(__name__)


class SSHSync:
    """Manages SSH/SFTP connection and file synchronization"""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize SSH sync with configuration

        Args:
            config: Dictionary with keys: host, port, username, remote_path
        """
        self.host = config['host']
        self.port = config.get('port', 22)
        self.username = config['username']
        self.remote_path = config['remote_path']

        self.ssh_client: Optional[paramiko.SSHClient] = None
        self.sftp_client: Optional[paramiko.SFTPClient] = None

        self._connect()

    def _connect(self):
        """Establish SSH/SFTP connection"""
        try:
            # Initialize SSH client
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Look for SSH key in default location
            key_path = Path.home() / '.ssh' / 'id_rsa'
            if not key_path.exists():
                key_path = Path.home() / '.ssh' / 'id_ed25519'

            logger.info(f"Connecting to {self.username}@{self.host}:{self.port}")

            # Try to connect with key
            if key_path.exists():
                logger.info(f"Using SSH key: {key_path}")
                self.ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=str(key_path),
                    timeout=10
                )
            else:
                logger.warning("No SSH key found, connection may fail")
                self.ssh_client.connect(
                    hostname=self.host,
                    port=self.port,
                    username=self.username,
                    look_for_keys=True,
                    timeout=10
                )

            # Open SFTP session
            self.sftp_client = self.ssh_client.open_sftp()

            # Ensure remote directory exists
            self._ensure_remote_directory()

            logger.info(f"Connected to {self.host}:{self.port}")

        except Exception as e:
            logger.error(f"Failed to connect to SSH server: {e}")
            self.ssh_client = None
            self.sftp_client = None
            raise

    def _ensure_remote_directory(self):
        """Create remote directory if it doesn't exist"""
        try:
            self.sftp_client.stat(self.remote_path)
        except FileNotFoundError:
            logger.info(f"Creating remote directory: {self.remote_path}")
            # Create parent directories recursively
            parts = self.remote_path.strip('/').split('/')
            current_path = ''
            for part in parts:
                current_path += '/' + part
                try:
                    self.sftp_client.stat(current_path)
                except FileNotFoundError:
                    self.sftp_client.mkdir(current_path)

    def is_connected(self) -> bool:
        """Check if SSH connection is active"""
        return self.ssh_client is not None and self.sftp_client is not None

    def sync_file(self, local_path: Path) -> bool:
        """
        Sync a single file to remote server

        Args:
            local_path: Path to local file

        Returns:
            True if successful, False otherwise
        """
        if not self.is_connected():
            logger.error("Not connected to SSH server")
            return False

        try:
            # Remote file path
            remote_file = f"{self.remote_path}/{local_path.name}"

            logger.info(f"Syncing {local_path.name} to {remote_file}")

            # Upload file
            self.sftp_client.put(str(local_path), remote_file)

            logger.info(f"Successfully synced {local_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error syncing file {local_path.name}: {e}")
            return False

    def sync_directory(self, local_dir: Path) -> int:
        """
        Sync all files in a directory to remote server

        Args:
            local_dir: Path to local directory

        Returns:
            Number of files successfully synced
        """
        if not self.is_connected():
            logger.error("Not connected to SSH server")
            return 0

        count = 0
        for file_path in local_dir.glob('*.md'):
            if self.sync_file(file_path):
                count += 1

        logger.info(f"Synced {count} files to remote server")
        return count

    def execute_command(self, command: str) -> tuple[int, str, str]:
        """
        Execute a command on the remote server

        Args:
            command: Command to execute

        Returns:
            Tuple of (exit_code, stdout, stderr)
        """
        if not self.is_connected():
            raise Exception("Not connected to SSH server")

        stdin, stdout, stderr = self.ssh_client.exec_command(command)
        exit_code = stdout.channel.recv_exit_status()

        return (
            exit_code,
            stdout.read().decode('utf-8'),
            stderr.read().decode('utf-8')
        )

    def close(self):
        """Close SSH/SFTP connection"""
        if self.sftp_client:
            self.sftp_client.close()
        if self.ssh_client:
            self.ssh_client.close()
        logger.info("SSH connection closed")

    def __del__(self):
        """Cleanup on deletion"""
        self.close()
