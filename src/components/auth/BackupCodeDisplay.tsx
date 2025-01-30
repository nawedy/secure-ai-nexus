import React, { useState } from 'react';
import { ClipboardIcon, DownloadIcon, CheckCircleIcon } from '@heroicons/react/24/outline';
import { saveAs } from 'file-saver';
import { logSecurityEvent } from '@/services/security';
import { useAuth } from '@/contexts/AuthContext';

interface BackupCodeDisplayProps {
  codes: string[];
  onComplete: () => Promise<void>;
}

export const BackupCodeDisplay: React.FC<BackupCodeDisplayProps> = ({
  codes,
  onComplete,
}) => {
  const [copied, setCopied] = useState(false);
  const [downloaded, setDownloaded] = useState(false);
  const [confirmed, setConfirmed] = useState(false);
  const { user } = useAuth();

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(codes.join('\n'));
      setCopied(true);
      await logSecurityEvent({
        type: 'BACKUP_CODES_COPIED',
        userId: user?.id,
        details: 'Backup codes copied to clipboard',
      });
    } catch (error) {
      console.error('Failed to copy codes:', error);
    }
  };

  const handleDownload = async () => {
    try {
      const content = [
        'SECUREAI PLATFORM - BACKUP CODES',
        '===============================',
        '',
        'Keep these codes safe and secure. Each code can only be used once.',
        '',
        ...codes,
        '',
        `Generated on: ${new Date().toISOString()}`,
        'For account: ' + user?.email,
      ].join('\n');

      const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
      saveAs(blob, 'secureai-backup-codes.txt');
      setDownloaded(true);

      await logSecurityEvent({
        type: 'BACKUP_CODES_DOWNLOADED',
        userId: user?.id,
        details: 'Backup codes downloaded as file',
      });
    } catch (error) {
      console.error('Failed to download codes:', error);
    }
  };

  const handleConfirmation = async () => {
    if (!copied && !downloaded) {
      return;
    }
    setConfirmed(true);
    await onComplete();
  };

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-medium text-gray-900">
          Backup Codes
        </h3>
        <p className="mt-1 text-sm text-gray-500">
          Save these backup codes in a secure location. Each code can only be used once.
        </p>
      </div>

      <div className="bg-gray-50 p-4 rounded-md font-mono text-sm">
        <div className="grid grid-cols-2 gap-4">
          {codes.map((code, index) => (
            <div
              key={code}
              className="p-2 bg-white rounded border border-gray-200 text-center"
            >
              {code}
            </div>
          ))}
        </div>
      </div>

      <div className="space-y-4">
        <button
          onClick={handleCopy}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <ClipboardIcon className="mr-2 h-5 w-5" />
          {copied ? 'Copied!' : 'Copy Codes'}
        </button>

        <button
          onClick={handleDownload}
          className="w-full flex items-center justify-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <DownloadIcon className="mr-2 h-5 w-5" />
          {downloaded ? 'Downloaded!' : 'Download Codes'}
        </button>
      </div>

      <div className="border-t border-gray-200 pt-6">
        <div className="flex items-center mb-4">
          <input
            id="confirm"
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            disabled={!copied && !downloaded}
          />
          <label htmlFor="confirm" className="ml-2 block text-sm text-gray-900">
            I have saved these backup codes in a secure location
          </label>
        </div>

        <button
          onClick={handleConfirmation}
          disabled={!confirmed}
          className="w-full flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          <CheckCircleIcon className="mr-2 h-5 w-5" />
          Complete Setup
        </button>
      </div>

      <div className="mt-4 text-xs text-gray-500 space-y-1">
        <p>• Each backup code can only be used once</p>
        <p>• Store these codes separately from your authenticator app</p>
        <p>• You can generate new backup codes at any time</p>
        <p>• Previous backup codes will be invalidated when new ones are generated</p>
      </div>
    </div>
  );
}; 