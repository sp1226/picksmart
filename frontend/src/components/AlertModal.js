import React from 'react';
import { CheckCircle, AlertCircle, X } from 'lucide-react';
import './AlertModal.css';

const AlertModal = ({ 
  isOpen, 
  message, 
  onClose, 
  onConfirm,  // props에 추가
  type = 'success' 
}) => {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-backdrop" onClick={onClose} />
      <div className="modal-container" role="dialog" aria-modal="true">
        <button
          onClick={onClose}
          className="modal-close-button"
        >
          <X size={20} />
        </button>
        
        <div className="modal-content">
          <div className="modal-icon">
            {type === 'success' ? (
              <div className="icon-circle success">
                <CheckCircle className="icon" />
              </div>
            ) : (
              <div className="icon-circle info">
                <AlertCircle className="icon" />
              </div>
            )}
          </div>
          
          <div className="modal-text">
            <h3>{type === 'success' ? '완료' : '알림'}</h3>
            <p>{message}</p>
          </div>

          <button
            onClick={() => {
              if (type === 'info' && onConfirm) {
                onConfirm();
              }
              onClose();
            }}
            className="modal-confirm-button"
            autoFocus
          >
            확인
          </button>
        </div>
      </div>
    </div>
  );
};

export default AlertModal;