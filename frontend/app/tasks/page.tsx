'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { api, Task, TaskCreate, TaskUpdate, TaskQueryParams } from '@/lib/api';
import { useTaskRefresh } from '@/contexts/TaskRefreshContext';
import { motion, AnimatePresence } from 'framer-motion';

export default function TasksPage() {
  const { isAuthenticated, isLoading: authLoading, getAccessToken, signout } = useAuth();
  const router = useRouter();
  const { onTasksChange } = useTaskRefresh();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  // New task form state
  const [newTaskTitle, setNewTaskTitle] = useState('');
  const [newTaskDescription, setNewTaskDescription] = useState('');
  const [newTaskPriority, setNewTaskPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [newTaskTags, setNewTaskTags] = useState('');
  const [newTaskDueAt, setNewTaskDueAt] = useState('');
  const [newTaskRemindAt, setNewTaskRemindAt] = useState('');
  const [newTaskRecurrence, setNewTaskRecurrence] = useState('');
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  // Edit task state
  const [editingTaskId, setEditingTaskId] = useState<string | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editPriority, setEditPriority] = useState<'low' | 'medium' | 'high'>('medium');
  const [editTags, setEditTags] = useState('');
  const [editDueAt, setEditDueAt] = useState('');
  const [editRemindAt, setEditRemindAt] = useState('');
  const [editRecurrence, setEditRecurrence] = useState('');
  const [isUpdating, setIsUpdating] = useState(false);

  // Filter, search, sort state
  const [filter, setFilter] = useState<'all' | 'incomplete' | 'complete'>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'created_at' | 'due_date' | 'priority'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');
  const [priorityFilter, setPriorityFilter] = useState<string>('');

  // Redirect to signin if not authenticated
  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/auth/signin');
    }
  }, [isAuthenticated, authLoading, router]);

  // Fetch tasks on mount and when filters change
  useEffect(() => {
    if (isAuthenticated) {
      fetchTasks();
    }
  }, [isAuthenticated, filter, sortBy, sortOrder, priorityFilter]);

  // Listen for task changes from ChatWidget
  useEffect(() => {
    if (!isAuthenticated) return;

    const unsubscribe = onTasksChange(() => {
      fetchTasks();
    });

    return unsubscribe;
  }, [isAuthenticated, onTasksChange]);

  const fetchTasks = async () => {
    try {
      setIsLoading(true);
      setError('');
      const accessToken = getAccessToken();
      if (!accessToken) {
        router.push('/auth/signin');
        return;
      }
      const params: TaskQueryParams = {
        sort_by: sortBy,
        order: sortOrder,
      };
      if (filter !== 'all') params.status = filter;
      if (priorityFilter) params.priority = priorityFilter;
      if (searchQuery.trim()) params.q = searchQuery.trim();
      const data = await api.getTasks(accessToken, params);
      setTasks(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch tasks');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!newTaskTitle.trim()) {
      setError('Task title is required');
      return;
    }

    try {
      setIsCreating(true);
      setError('');
      const accessToken = getAccessToken();
      if (!accessToken) {
        router.push('/auth/signin');
        return;
      }

      const parsedTags = newTaskTags
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

      // datetime-local gives "YYYY-MM-DDTHH:mm" — append ":00" for ISO 8601
      const formatDt = (v: string) => v ? (v.length === 16 ? v + ':00' : v) : undefined;

      const newTask: TaskCreate = {
        title: newTaskTitle,
        description: newTaskDescription || undefined,
        priority: newTaskPriority,
        tags: parsedTags.length > 0 ? parsedTags : undefined,
        due_at: formatDt(newTaskDueAt),
        remind_at: formatDt(newTaskRemindAt),
        recurrence_pattern: (newTaskRecurrence as 'daily' | 'weekly' | 'monthly') || undefined,
      };

      await api.createTask(accessToken, newTask);

      // Clear form
      setNewTaskTitle('');
      setNewTaskDescription('');
      setNewTaskPriority('medium');
      setNewTaskTags('');
      setNewTaskDueAt('');
      setNewTaskRemindAt('');
      setNewTaskRecurrence('');
      setShowAdvanced(false);

      // Refresh task list
      await fetchTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create task');
    } finally {
      setIsCreating(false);
    }
  };

  const handleToggleComplete = async (taskId: string) => {
    try {
      setError('');
      const accessToken = getAccessToken();
      if (!accessToken) {
        router.push('/auth/signin');
        return;
      }

      // Optimistic update
      setTasks(tasks.map(task =>
        task.id === taskId
          ? { ...task, status: task.status === 'complete' ? 'incomplete' : 'complete' }
          : task
      ));

      await api.toggleTaskComplete(accessToken, taskId);

      // Refresh to get server state
      await fetchTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle task');
      // Revert optimistic update on error
      await fetchTasks();
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    if (!confirm('Are you sure you want to delete this task?')) {
      return;
    }

    try {
      setError('');
      const accessToken = getAccessToken();
      if (!accessToken) {
        router.push('/auth/signin');
        return;
      }

      await api.deleteTask(accessToken, taskId);

      // Refresh task list
      await fetchTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete task');
    }
  };

  const handleStartEdit = (task: Task) => {
    setEditingTaskId(task.id);
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setEditPriority((task.priority as 'low' | 'medium' | 'high') || 'medium');
    setEditTags(task.tags?.join(', ') || '');
    setEditDueAt(task.due_at ? task.due_at.slice(0, 16) : '');
    setEditRemindAt(task.remind_at ? task.remind_at.slice(0, 16) : '');
    setEditRecurrence(task.recurrence_pattern || '');
  };

  const handleCancelEdit = () => {
    setEditingTaskId(null);
    setEditTitle('');
    setEditDescription('');
    setEditPriority('medium');
    setEditTags('');
    setEditDueAt('');
    setEditRemindAt('');
    setEditRecurrence('');
  };

  const handleUpdateTask = async (taskId: string) => {
    if (!editTitle.trim()) {
      setError('Task title is required');
      return;
    }

    try {
      setIsUpdating(true);
      setError('');
      const accessToken = getAccessToken();
      if (!accessToken) {
        router.push('/auth/signin');
        return;
      }

      const parsedEditTags = editTags
        .split(',')
        .map(t => t.trim())
        .filter(Boolean);

      const formatDt = (v: string) => v ? (v.length === 16 ? v + ':00' : v) : undefined;

      const updateData: TaskUpdate = {
        title: editTitle,
        description: editDescription || undefined,
        priority: editPriority,
        tags: parsedEditTags,
        due_at: formatDt(editDueAt),
        remind_at: formatDt(editRemindAt),
        recurrence_pattern: (editRecurrence as 'daily' | 'weekly' | 'monthly') || undefined,
      };

      await api.updateTask(accessToken, taskId, updateData);

      // Reset edit state
      handleCancelEdit();

      // Refresh task list
      await fetchTasks();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update task');
    } finally {
      setIsUpdating(false);
    }
  };

  // Tasks are already filtered by the backend based on query params.
  // Stats are computed from current result set.
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === 'complete').length;
  const incompleteTasks = tasks.filter(t => t.status === 'incomplete').length;

  // Debounced search handler
  useEffect(() => {
    const timeout = setTimeout(() => {
      if (isAuthenticated) fetchTasks();
    }, 400);
    return () => clearTimeout(timeout);
  }, [searchQuery]);

  // Show loading while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="animate-spin h-12 w-12 text-blue-600 mx-auto"
            fill="none"
            viewBox="0 0 24 24"
          >
            <circle
              className="opacity-25"
              cx="12"
              cy="12"
              r="10"
              stroke="currentColor"
              strokeWidth="4"
            />
            <path
              className="opacity-75"
              fill="currentColor"
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render if not authenticated (will redirect)
  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Navigation */}
      <nav className="bg-white/80 backdrop-blur-md shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <Link href="/" className="flex items-center group">
                <svg
                  className="h-8 w-8 text-blue-600 group-hover:text-blue-700 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"
                  />
                </svg>
                <span className="ml-2 text-xl font-bold text-gray-900 group-hover:text-gray-700 transition-colors">
                  TaskFlow
                </span>
              </Link>
            </div>
            <div className="flex items-center">
              <button
                onClick={signout}
                className="inline-flex items-center px-3 py-2 border border-gray-300 text-sm font-medium rounded-lg text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all"
              >
                <svg
                  className="h-4 w-4 md:mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                  />
                </svg>
                <span className="hidden md:inline">Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        {/* Header with Stats */}
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-2">
            My Tasks
          </h1>
          <p className="text-lg text-gray-600 mb-6">
            Stay organized and productive with your task dashboard
          </p>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-blue-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="h-6 w-6 text-blue-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                      />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Total Tasks</p>
                  <p className="text-2xl font-bold text-gray-900">{totalTasks}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="h-6 w-6 text-green-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">Completed</p>
                  <p className="text-2xl font-bold text-gray-900">{completedTasks}</p>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-md border border-gray-100">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-12 w-12 bg-yellow-100 rounded-lg flex items-center justify-center">
                    <svg
                      className="h-6 w-6 text-yellow-600"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                  </div>
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-600">In Progress</p>
                  <p className="text-2xl font-bold text-gray-900">{incompleteTasks}</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 rounded-lg bg-red-50 border border-red-200 p-4">
            <div className="flex">
              <svg
                className="h-5 w-5 text-red-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              <div className="ml-3">
                <p className="text-sm font-medium text-red-800">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* New Task Form */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6 border border-gray-100">
          <div className="flex items-center mb-4">
            <svg
              className="h-6 w-6 text-blue-600 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v16m8-8H4"
              />
            </svg>
            <h2 className="text-xl font-semibold text-gray-900">Create New Task</h2>
          </div>
          <form onSubmit={handleCreateTask}>
            <div className="space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Task Title
                </label>
                <input
                  type="text"
                  id="title"
                  value={newTaskTitle}
                  onChange={(e) => setNewTaskTitle(e.target.value)}
                  className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                  placeholder="What needs to be done?"
                  required
                />
              </div>
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description <span className="text-gray-500 font-normal">(optional)</span>
                </label>
                <textarea
                  id="description"
                  value={newTaskDescription}
                  onChange={(e) => setNewTaskDescription(e.target.value)}
                  rows={2}
                  className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                  placeholder="Add more details about this task..."
                />
              </div>

              {/* Priority & Tags row */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label htmlFor="priority" className="block text-sm font-medium text-gray-700">
                    Priority
                  </label>
                  <select
                    id="priority"
                    value={newTaskPriority}
                    onChange={(e) => setNewTaskPriority(e.target.value as 'low' | 'medium' | 'high')}
                    className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                  >
                    <option value="low">Low</option>
                    <option value="medium">Medium</option>
                    <option value="high">High</option>
                  </select>
                </div>
                <div>
                  <label htmlFor="tags" className="block text-sm font-medium text-gray-700">
                    Tags <span className="text-gray-500 font-normal">(comma-separated)</span>
                  </label>
                  <input
                    type="text"
                    id="tags"
                    value={newTaskTags}
                    onChange={(e) => setNewTaskTags(e.target.value)}
                    className="mt-1 block w-full px-4 py-3 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                    placeholder="e.g. work, urgent, shopping"
                  />
                </div>
              </div>

              {/* Advanced Options Toggle */}
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="text-sm text-blue-600 hover:text-blue-800 font-medium transition-colors"
              >
                {showAdvanced ? 'Hide advanced options' : 'Show advanced options (due date, reminder, recurrence)'}
              </button>

              {showAdvanced && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
                  <div>
                    <label htmlFor="dueAt" className="block text-sm font-medium text-gray-700">
                      Due Date
                    </label>
                    <input
                      type="datetime-local"
                      id="dueAt"
                      value={newTaskDueAt}
                      onChange={(e) => setNewTaskDueAt(e.target.value)}
                      className="mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor="remindAt" className="block text-sm font-medium text-gray-700">
                      Reminder
                    </label>
                    <input
                      type="datetime-local"
                      id="remindAt"
                      value={newTaskRemindAt}
                      onChange={(e) => setNewTaskRemindAt(e.target.value)}
                      className="mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                    />
                  </div>
                  <div>
                    <label htmlFor="recurrence" className="block text-sm font-medium text-gray-700">
                      Recurrence
                    </label>
                    <select
                      id="recurrence"
                      value={newTaskRecurrence}
                      onChange={(e) => setNewTaskRecurrence(e.target.value)}
                      className="mt-1 block w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                    >
                      <option value="">None</option>
                      <option value="daily">Daily</option>
                      <option value="weekly">Weekly</option>
                      <option value="monthly">Monthly</option>
                    </select>
                  </div>
                </div>
              )}

              <div>
                <button
                  type="submit"
                  disabled={isCreating}
                  className="w-full flex justify-center items-center py-3 px-4 border border-transparent rounded-lg shadow-md text-sm font-medium text-white bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed transition-all transform hover:scale-[1.01] active:scale-[0.99]"
                >
                  {isCreating ? (
                    <>
                      <svg
                        className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        />
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        />
                      </svg>
                      Creating...
                    </>
                  ) : (
                    <>
                      <svg
                        className="h-5 w-5 mr-2"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth={2}
                          d="M12 4v16m8-8H4"
                        />
                      </svg>
                      Add Task
                    </>
                  )}
                </button>
              </div>
            </div>
          </form>
        </div>

        {/* Task List */}
        <div className="bg-white rounded-2xl shadow-xl p-4 md:p-6 border border-gray-100">
          {/* Search Bar */}
          <div className="mb-4">
            <div className="relative">
              <svg className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search tasks by title or description..."
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg shadow-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
              />
            </div>
          </div>

          <div className="flex flex-col gap-4 mb-6">
            {/* Filter Tabs row */}
            <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
              <h2 className="text-xl font-semibold text-gray-900">Your Tasks</h2>
              <div className="flex flex-wrap gap-2">
                <button
                  onClick={() => setFilter('all')}
                  className={`px-3 md:px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    filter === 'all'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  All ({totalTasks})
                </button>
                <button
                  onClick={() => setFilter('incomplete')}
                  className={`px-3 md:px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    filter === 'incomplete'
                      ? 'bg-yellow-100 text-yellow-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Active ({incompleteTasks})
                </button>
                <button
                  onClick={() => setFilter('complete')}
                  className={`px-3 md:px-4 py-2 text-sm font-medium rounded-lg transition-all ${
                    filter === 'complete'
                      ? 'bg-green-100 text-green-700'
                      : 'text-gray-600 hover:bg-gray-100'
                  }`}
                >
                  Done ({completedTasks})
                </button>
              </div>
            </div>

            {/* Sort & Priority Filter row */}
            <div className="flex flex-wrap items-center gap-3">
              <div className="flex items-center gap-2">
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Sort</label>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'created_at' | 'due_date' | 'priority')}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="created_at">Date Created</option>
                  <option value="due_date">Due Date</option>
                  <option value="priority">Priority</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'desc' ? 'asc' : 'desc')}
                  className="p-1.5 border border-gray-300 rounded-lg text-gray-600 hover:bg-gray-50 transition-all"
                  title={sortOrder === 'desc' ? 'Descending' : 'Ascending'}
                >
                  {sortOrder === 'desc' ? (
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                  ) : (
                    <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" /></svg>
                  )}
                </button>
              </div>
              <div className="flex items-center gap-2">
                <label className="text-xs font-medium text-gray-500 uppercase tracking-wide">Priority</label>
                <select
                  value={priorityFilter}
                  onChange={(e) => setPriorityFilter(e.target.value)}
                  className="px-3 py-1.5 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">All</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
            </div>
          </div>

          {isLoading ? (
            <div className="text-center py-12">
              <svg
                className="animate-spin h-10 w-10 text-blue-600 mx-auto"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <p className="mt-4 text-gray-600">Loading tasks...</p>
            </div>
          ) : tasks.length === 0 ? (
            <div className="text-center py-12">
              <svg
                className="h-16 w-16 text-gray-300 mx-auto mb-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
                />
              </svg>
              <p className="text-gray-500 text-lg">
                {searchQuery.trim()
                  ? 'No tasks match your search.'
                  : filter === 'all'
                  ? 'No tasks yet. Create your first task above!'
                  : filter === 'complete'
                  ? 'No completed tasks yet. Keep working!'
                  : 'No active tasks. Great job!'
                }
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              <AnimatePresence mode="popLayout">
                {tasks.map((task) => (
                  <motion.div
                    key={task.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    transition={{ duration: 0.2 }}
                    layout
                    className={`border rounded-xl p-5 transition-all ${
                      task.status === 'complete'
                        ? 'border-green-200 bg-green-50/50'
                        : 'border-gray-200 bg-white hover:shadow-lg hover:border-blue-200'
                    }`}
                  >
                  {editingTaskId === task.id ? (
                    // Edit mode
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Task Title</label>
                        <input
                          type="text"
                          value={editTitle}
                          onChange={(e) => setEditTitle(e.target.value)}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          placeholder="Enter task title"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                        <textarea
                          value={editDescription}
                          onChange={(e) => setEditDescription(e.target.value)}
                          rows={2}
                          className="w-full px-4 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          placeholder="Enter task description"
                        />
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                          <select
                            value={editPriority}
                            onChange={(e) => setEditPriority(e.target.value as 'low' | 'medium' | 'high')}
                            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          >
                            <option value="low">Low</option>
                            <option value="medium">Medium</option>
                            <option value="high">High</option>
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Tags (comma-separated)</label>
                          <input
                            type="text"
                            value={editTags}
                            onChange={(e) => setEditTags(e.target.value)}
                            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                            placeholder="e.g. work, urgent"
                          />
                        </div>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Due Date</label>
                          <input
                            type="datetime-local"
                            value={editDueAt}
                            onChange={(e) => setEditDueAt(e.target.value)}
                            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Reminder</label>
                          <input
                            type="datetime-local"
                            value={editRemindAt}
                            onChange={(e) => setEditRemindAt(e.target.value)}
                            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          />
                        </div>
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-1">Recurrence</label>
                          <select
                            value={editRecurrence}
                            onChange={(e) => setEditRecurrence(e.target.value)}
                            className="w-full px-3 py-2.5 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all sm:text-sm"
                          >
                            <option value="">None</option>
                            <option value="daily">Daily</option>
                            <option value="weekly">Weekly</option>
                            <option value="monthly">Monthly</option>
                          </select>
                        </div>
                      </div>
                      <div className="flex gap-3">
                        <button
                          onClick={() => handleUpdateTask(task.id)}
                          disabled={isUpdating}
                          className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-lg hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:from-gray-400 disabled:to-gray-400 disabled:cursor-not-allowed font-medium transition-all"
                        >
                          {isUpdating ? 'Saving...' : 'Save Changes'}
                        </button>
                        <button
                          onClick={handleCancelEdit}
                          disabled={isUpdating}
                          className="flex-1 px-4 py-3 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-gray-500 disabled:opacity-50 font-medium transition-all"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View mode
                    <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                      <div className="flex items-start space-x-3 md:space-x-4 flex-1 min-w-0">
                        <input
                          type="checkbox"
                          checked={task.status === 'complete'}
                          onChange={() => handleToggleComplete(task.id)}
                          className="mt-1 h-5 w-5 md:h-6 md:w-6 text-blue-600 focus:ring-blue-500 border-gray-300 rounded cursor-pointer transition-all flex-shrink-0"
                        />
                        <div className="flex-1 min-w-0">
                          <h3
                            className={`text-base md:text-lg font-semibold break-words ${
                              task.status === 'complete'
                                ? 'line-through text-gray-500'
                                : 'text-gray-900'
                            }`}
                          >
                            {task.title}
                          </h3>
                          {task.description && (
                            <p
                              className={`mt-1 text-sm break-words ${
                                task.status === 'complete'
                                  ? 'line-through text-gray-400'
                                  : 'text-gray-600'
                              }`}
                            >
                              {task.description}
                            </p>
                          )}
                          <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-gray-500">
                            {/* Status badge */}
                            <span className={`inline-flex items-center px-2 md:px-3 py-1 rounded-full text-xs font-medium ${
                              task.status === 'complete'
                                ? 'bg-green-100 text-green-700'
                                : 'bg-yellow-100 text-yellow-700'
                            }`}>
                              {task.status === 'complete' ? (
                                <>
                                  <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                  </svg>
                                  Completed
                                </>
                              ) : (
                                <>
                                  <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
                                  </svg>
                                  In Progress
                                </>
                              )}
                            </span>

                            {/* Priority badge */}
                            <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                              task.priority === 'high' ? 'bg-red-100 text-red-700' :
                              task.priority === 'medium' ? 'bg-orange-100 text-orange-700' :
                              'bg-gray-100 text-gray-600'
                            }`}>
                              {(task.priority || 'medium').charAt(0).toUpperCase() + (task.priority || 'medium').slice(1)}
                            </span>

                            {/* Due date */}
                            {task.due_at && (
                              <span className={`flex items-center ${
                                new Date(task.due_at) < new Date() && task.status !== 'complete'
                                  ? 'text-red-600 font-medium' : 'text-gray-500'
                              }`}>
                                <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                Due {new Date(task.due_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                              </span>
                            )}

                            {/* Recurrence indicator */}
                            {task.recurrence_pattern && (
                              <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-700">
                                <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                                </svg>
                                {task.recurrence_pattern}
                              </span>
                            )}

                            {/* Reminder indicator */}
                            {task.remind_at && !task.reminder_sent && (
                              <span className="inline-flex items-center text-blue-600">
                                <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                                </svg>
                                Reminder
                              </span>
                            )}

                            {/* Created date */}
                            <span className="flex items-center">
                              <svg className="h-3 w-3 mr-1 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                              </svg>
                              <span className="truncate">
                                {new Date(task.created_at).toLocaleDateString('en-US', {
                                  month: 'short',
                                  day: 'numeric',
                                  year: 'numeric'
                                })}
                              </span>
                            </span>
                          </div>

                          {/* Tags */}
                          {task.tags && task.tags.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1.5">
                              {task.tags.map((tag) => (
                                <span
                                  key={tag}
                                  className="inline-flex items-center px-2 py-0.5 rounded-md text-xs font-medium bg-blue-50 text-blue-700 border border-blue-200"
                                >
                                  {tag}
                                </span>
                              ))}
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="flex gap-2 md:ml-4 flex-shrink-0">
                        <button
                          onClick={() => handleStartEdit(task)}
                          className="flex-1 md:flex-none px-4 md:px-0 md:p-2 py-2 text-sm md:text-base font-medium md:font-normal text-blue-600 hover:bg-blue-50 rounded-lg focus:outline-none transition-all border md:border-0 border-blue-200"
                          title="Edit task"
                        >
                          <svg
                            className="h-5 w-5 mx-auto md:mx-0"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                            />
                          </svg>
                        </button>
                        <button
                          onClick={() => handleDeleteTask(task.id)}
                          className="flex-1 md:flex-none px-4 md:px-0 md:p-2 py-2 text-sm md:text-base font-medium md:font-normal text-red-600 hover:bg-red-50 rounded-lg focus:outline-none transition-all border md:border-0 border-red-200"
                          title="Delete task"
                        >
                          <svg
                            className="h-5 w-5 mx-auto md:mx-0"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              strokeLinecap="round"
                              strokeLinejoin="round"
                              strokeWidth={2}
                              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                            />
                          </svg>
                        </button>
                      </div>
                    </div>
                  )}
                  </motion.div>
                ))}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
