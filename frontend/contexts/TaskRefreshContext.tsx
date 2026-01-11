"use client";

import React, { createContext, useContext, useState, useCallback } from "react";

interface TaskRefreshContextType {
  refreshTasks: () => void;
  onTasksChange: (callback: () => void) => () => void;
}

const TaskRefreshContext = createContext<TaskRefreshContextType | undefined>(
  undefined
);

export function TaskRefreshProvider({ children }: { children: React.ReactNode }) {
  const [listeners, setListeners] = useState<Set<() => void>>(new Set());

  const refreshTasks = useCallback(() => {
    // Notify all registered listeners
    listeners.forEach((callback) => callback());
  }, [listeners]);

  const onTasksChange = useCallback(
    (callback: () => void) => {
      setListeners((prev) => new Set([...prev, callback]));

      // Return cleanup function
      return () => {
        setListeners((prev) => {
          const next = new Set(prev);
          next.delete(callback);
          return next;
        });
      };
    },
    []
  );

  return (
    <TaskRefreshContext.Provider value={{ refreshTasks, onTasksChange }}>
      {children}
    </TaskRefreshContext.Provider>
  );
}

export function useTaskRefresh() {
  const context = useContext(TaskRefreshContext);
  if (context === undefined) {
    throw new Error("useTaskRefresh must be used within a TaskRefreshProvider");
  }
  return context;
}
