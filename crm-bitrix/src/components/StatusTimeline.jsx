import React from 'react';

const StatusTimeline = ({ history }) => {
  if (!history || history.length === 0) {
    return (
      <div className="text-center py-8">
        <p className="text-sm font-['Open_Sans'] text-gray-placeholder">
          Нет истории изменений
        </p>
      </div>
    );
  }

  const getStatusColor = (status) => {
    const statusColorMap = {
      new: 'bg-status-new',
      paid: 'bg-blue-500',
      accepted: 'bg-purple-500',
      assembled: 'bg-status-assembled',
      in_delivery: 'bg-green-400',
      delivered: 'bg-green-success',
      cancelled: 'bg-gray-400',
      default: 'bg-gray-neutral'
    };
    return statusColorMap[status] || statusColorMap.default;
  };

  return (
    <div className="space-y-0">
      {history.map((event, index) => {
        const isLast = index === history.length - 1;

        return (
          <div key={index} className="flex gap-4">
            {/* Timeline column with dot and line */}
            <div className="flex flex-col items-center">
              {/* Dot */}
              <div className={`w-3 h-3 rounded-full ${getStatusColor(event.status)} flex-shrink-0 mt-1.5`} />

              {/* Vertical line */}
              {!isLast && (
                <div className="w-0.5 h-full bg-gray-border flex-grow my-1" />
              )}
            </div>

            {/* Content column */}
            <div className={`flex-1 ${isLast ? 'pb-0' : 'pb-6'}`}>
              {/* Status label */}
              <div className="font-['Open_Sans'] font-semibold text-base text-black mb-1">
                {event.statusLabel || event.status}
              </div>

              {/* Date and time */}
              <div className="font-['Open_Sans'] text-sm text-gray-disabled mb-1">
                {event.date} в {event.time}
              </div>

              {/* User who made the change */}
              {event.user && (
                <div className="font-['Open_Sans'] text-sm text-gray-placeholder">
                  {event.user}
                </div>
              )}

              {/* Optional notes */}
              {event.notes && (
                <div className="mt-2 font-['Open_Sans'] text-sm text-gray-600 italic">
                  {event.notes}
                </div>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default StatusTimeline;
