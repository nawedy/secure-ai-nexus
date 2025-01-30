import React from 'react';
import QRCode from 'qrcode.react';

interface QRCodeDisplayProps {
  uri: string;
  size?: number;
  className?: string;
}

export const QRCodeDisplay: React.FC<QRCodeDisplayProps> = ({
  uri,
  size = 200,
  className = '',
}) => {
  return (
    <div className={`bg-white p-4 rounded-lg ${className}`}>
      <QRCode
        value={uri}
        size={size}
        level="H"
        includeMargin={true}
        renderAs="svg"
      />
      <p className="mt-2 text-sm text-gray-500 text-center">
        Scan with your authenticator app
      </p>
    </div>
  );
}; 