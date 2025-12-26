import React, { useState } from 'react';
import { AlertCircle, Mic, FileText, Clock, CheckCircle, AlertTriangle } from 'lucide-react';

// ==================== APP.JSX (Router) ====================
function App() {
  const [currentPage, setCurrentPage] = useState('login');
  const [loggedInUser, setLoggedInUser] = useState(null);

  const navigate = (page, user = null) => {
    setCurrentPage(page);
    if (user) setLoggedInUser(user);
  };

  const handleLogout = () => {
    setLoggedInUser(null);
    setCurrentPage('login');
  };

  return (
    <div>
      {currentPage === 'login' && <LoginPage onLogin={navigate} />}
      {currentPage === 'user' && <UserDashboard user={loggedInUser} onLogout={handleLogout} />}
      {currentPage === 'department' && <DepartmentDashboard user={loggedInUser} onLogout={handleLogout} />}
    </div>
  );
}

// ==================== LOGIN PAGE ====================
function LoginPage({ onLogin }) {
  const [userType, setUserType] = useState(null);
  const [credentials, setCredentials] = useState({ username: '', password: '' });
  const [error, setError] = useState('');

  const departments = [
    { name: 'Police', password: 'police123' },
    { name: 'WaterBoard', password: 'water123' },
    { name: 'Electricity', password: 'electric123' }
  ];

  const mockUsers = [
    { username: 'user1', password: 'pass123' },
    { username: 'user2', password: 'pass456' },
    { username: 'demo', password: 'demo123' }
  ];

  const handleUserTypeSelect = (type) => {
    setUserType(type);
    setError('');
    setCredentials({ username: '', password: '' });
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setCredentials(prev => ({ ...prev, [name]: value }));
    setError('');
  };

  const handleUserLogin = () => {
    if (!credentials.username.trim()) {
      setError('Please enter your username');
      return;
    }
    if (!credentials.password.trim()) {
      setError('Please enter your password');
      return;
    }

    const user = mockUsers.find(
      u => u.username === credentials.username && u.password === credentials.password
    );

    if (!user) {
      setError('Invalid username or password');
      return;
    }

    onLogin('user', { type: 'user', username: credentials.username });
  };

  const handleDepartmentLogin = () => {
    if (!credentials.username) {
      setError('Please select a department');
      return;
    }
    if (!credentials.password.trim()) {
      setError('Please enter department password');
      return;
    }

    const dept = departments.find(
      d => d.name === credentials.username && d.password === credentials.password
    );

    if (!dept) {
      setError('Invalid department or password');
      return;
    }

    onLogin('department', { type: 'department', department: credentials.username });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-800 mb-2">
            Public Grievance System
          </h1>
          <p className="text-gray-600">Select your role to continue</p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl p-8">
          {!userType && (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-gray-700 mb-6 text-center">
                Login as...
              </h2>
              
              <button
                onClick={() => handleUserTypeSelect('user')}
                className="w-full py-6 px-6 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-xl hover:from-blue-600 hover:to-blue-700 transition-all transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">👤</div>
                <div className="text-xl font-semibold">User</div>
                <div className="text-sm text-blue-100 mt-1">File a complaint</div>
              </button>

              <button
                onClick={() => handleUserTypeSelect('department')}
                className="w-full py-6 px-6 bg-gradient-to-r from-indigo-500 to-indigo-600 text-white rounded-xl hover:from-indigo-600 hover:to-indigo-700 transition-all transform hover:scale-105 shadow-lg"
              >
                <div className="text-2xl mb-2">🏛️</div>
                <div className="text-xl font-semibold">Department</div>
                <div className="text-sm text-indigo-100 mt-1">Manage complaints</div>
              </button>
            </div>
          )}

          {userType === 'user' && (
            <div className="space-y-6">
              <button
                onClick={() => setUserType(null)}
                className="text-gray-500 hover:text-gray-700 mb-4"
              >
                ← Back
              </button>
              
              <div className="text-center mb-6">
                <div className="text-5xl mb-4">👤</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">User Login</h2>
                <p className="text-gray-600">Enter your credentials</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Username</label>
                  <input
                    type="text"
                    name="username"
                    value={credentials.username}
                    onChange={handleInputChange}
                    placeholder="Enter your username"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
                  <input
                    type="password"
                    name="password"
                    value={credentials.password}
                    onChange={handleInputChange}
                    placeholder="Enter your password"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                  />
                </div>

                {error && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    <AlertCircle size={18} />
                    <span className="text-sm">{error}</span>
                  </div>
                )}

                <button
                  onClick={handleUserLogin}
                  className="w-full py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-semibold text-lg mt-6"
                >
                  Login
                </button>

                <div className="text-center text-sm text-gray-500 mt-4">
                  Demo: user1 / pass123
                </div>
              </div>
            </div>
          )}

          {userType === 'department' && (
            <div className="space-y-6">
              <button
                onClick={() => setUserType(null)}
                className="text-gray-500 hover:text-gray-700 mb-4"
              >
                ← Back
              </button>
              
              <div className="text-center mb-6">
                <div className="text-5xl mb-4">🏛️</div>
                <h2 className="text-2xl font-bold text-gray-800 mb-2">Department Login</h2>
                <p className="text-gray-600">Enter department credentials</p>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Department Name</label>
                  <select
                    name="username"
                    value={credentials.username}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  >
                    <option value="">Select Department</option>
                    {departments.map(dept => (
                      <option key={dept.name} value={dept.name}>{dept.name}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Department Password</label>
                  <input
                    type="password"
                    name="password"
                    value={credentials.password}
                    onChange={handleInputChange}
                    placeholder="Enter department password"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                  />
                </div>

                {error && (
                  <div className="flex items-center gap-2 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700">
                    <AlertCircle size={18} />
                    <span className="text-sm">{error}</span>
                  </div>
                )}

                <button
                  onClick={handleDepartmentLogin}
                  className="w-full py-4 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-semibold text-lg mt-6"
                >
                  Login
                </button>

                <div className="text-center text-sm text-gray-500 mt-4">
                  Demo: Police / police123
                </div>
              </div>
            </div>
          )}
        </div>

        <p className="text-center text-gray-500 text-sm mt-6">
          Secure Login • Government Portal
        </p>
      </div>
    </div>
  );
}

// ==================== USER DASHBOARD ====================
function UserDashboard({ user, onLogout }) {
  const [activeTab, setActiveTab] = useState('file');
  const [complaintType, setComplaintType] = useState('text');
  const [complaintText, setComplaintText] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [submitStatus, setSubmitStatus] = useState(null);

  // Mock user complaints
  const [myComplaints] = useState([
    {
      id: 'C001',
      text: 'Street light not working on Main Road',
      department: 'Electricity',
      status: 'In Progress',
      urgency: 4,
      date: '2024-12-24'
    },
    {
      id: 'C002',
      text: 'Water supply issue in Sector 5',
      department: 'WaterBoard',
      status: 'Resolved',
      urgency: 7,
      date: '2024-12-20'
    }
  ]);

  const handleSubmitComplaint = () => {
    if (!complaintText.trim()) {
      setSubmitStatus('error');
      return;
    }

    // Simulate API call
    setSubmitStatus('success');
    setTimeout(() => {
      setComplaintText('');
      setSubmitStatus(null);
    }, 3000);
  };

  const handleRecordAudio = () => {
    setIsRecording(!isRecording);
    // Simulate recording
    if (!isRecording) {
      setTimeout(() => setIsRecording(false), 5000);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">User Dashboard</h1>
              <p className="text-gray-600 mt-2">
                <span className="font-semibold">Username:</span> {user.username}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          </div>

          {/* Tabs */}
          <div className="flex gap-4 mb-6 border-b">
            <button
              onClick={() => setActiveTab('file')}
              className={`px-6 py-3 font-semibold transition-colors ${
                activeTab === 'file'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              File Complaint
            </button>
            <button
              onClick={() => setActiveTab('track')}
              className={`px-6 py-3 font-semibold transition-colors ${
                activeTab === 'track'
                  ? 'text-blue-600 border-b-2 border-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              My Complaints
            </button>
          </div>

          {/* File Complaint Tab */}
          {activeTab === 'file' && (
            <div className="space-y-6">
              <div className="flex gap-4 mb-6">
                <button
                  onClick={() => setComplaintType('text')}
                  className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
                    complaintType === 'text'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <FileText className="inline mr-2" size={20} />
                  Text Complaint
                </button>
                <button
                  onClick={() => setComplaintType('audio')}
                  className={`flex-1 py-4 rounded-xl font-semibold transition-all ${
                    complaintType === 'audio'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <Mic className="inline mr-2" size={20} />
                  Voice Complaint
                </button>
              </div>

              {complaintType === 'text' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Describe your complaint
                  </label>
                  <textarea
                    value={complaintText}
                    onChange={(e) => setComplaintText(e.target.value)}
                    placeholder="Enter your complaint details here..."
                    rows={6}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                  />
                </div>
              )}

              {complaintType === 'audio' && (
                <div className="text-center py-12 bg-gray-50 rounded-xl">
                  <button
                    onClick={handleRecordAudio}
                    className={`px-8 py-4 rounded-full font-semibold transition-all ${
                      isRecording
                        ? 'bg-red-600 text-white animate-pulse'
                        : 'bg-blue-600 text-white hover:bg-blue-700'
                    }`}
                  >
                    <Mic className="inline mr-2" size={24} />
                    {isRecording ? 'Recording... (5s)' : 'Start Recording'}
                  </button>
                  <p className="text-gray-600 mt-4">Click to record your complaint</p>
                </div>
              )}

              {submitStatus === 'success' && (
                <div className="flex items-center gap-2 p-4 bg-green-50 border border-green-200 rounded-lg text-green-700">
                  <CheckCircle size={20} />
                  <span>Complaint submitted successfully!</span>
                </div>
              )}

              {submitStatus === 'error' && (
                <div className="flex items-center gap-2 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
                  <AlertCircle size={20} />
                  <span>Please enter a complaint before submitting</span>
                </div>
              )}

              <button
                onClick={handleSubmitComplaint}
                className="w-full py-4 bg-blue-600 text-white rounded-xl hover:bg-blue-700 transition-colors font-semibold text-lg"
              >
                Submit Complaint
              </button>
            </div>
          )}

          {/* Track Complaints Tab */}
          {activeTab === 'track' && (
            <div className="space-y-4">
              {myComplaints.map((complaint) => (
                <div
                  key={complaint.id}
                  className="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-sm font-semibold text-gray-500">
                          {complaint.id}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-semibold ${
                            complaint.status === 'Resolved'
                              ? 'bg-green-100 text-green-700'
                              : complaint.status === 'In Progress'
                              ? 'bg-blue-100 text-blue-700'
                              : 'bg-yellow-100 text-yellow-700'
                          }`}
                        >
                          {complaint.status}
                        </span>
                      </div>
                      <p className="text-gray-800 font-medium mb-2">{complaint.text}</p>
                      <div className="flex items-center gap-4 text-sm text-gray-600">
                        <span>Department: {complaint.department}</span>
                        <span>•</span>
                        <span>Urgency: {complaint.urgency}/10</span>
                        <span>•</span>
                        <span>{complaint.date}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 text-sm text-gray-500">
                    <Clock size={16} />
                    <span>Last updated 2 hours ago</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// ==================== DEPARTMENT DASHBOARD ====================
function DepartmentDashboard({ user, onLogout }) {
  const [selectedComplaint, setSelectedComplaint] = useState(null);
  const [response, setResponse] = useState('');

  // Mock complaints with priority
  const complaints = [
    {
      id: 'C002',
      text: 'Major fire at garbage dump, children affected',
      department: 'Fire',
      urgency: 9,
      escalated: true,
      sentiment: 'urgent',
      date: '2024-12-21',
      status: 'Pending'
    },
    {
      id: 'C005',
      text: 'Cybercrime - identity theft reported',
      department: 'Police',
      urgency: 8,
      escalated: true,
      sentiment: 'distressed',
      date: '2024-12-21',
      status: 'Pending'
    },
    {
      id: 'C003',
      text: 'Water supply contaminated with dirt and debris',
      department: 'WaterBoard',
      urgency: 7,
      escalated: true,
      sentiment: 'concerned',
      date: '2024-12-20',
      status: 'Pending'
    },
    {
      id: 'C004',
      text: 'Pothole on highway causing accidents',
      department: 'RoadTransport',
      urgency: 6,
      escalated: false,
      sentiment: 'worried',
      date: '2024-12-22',
      status: 'Pending'
    },
    {
      id: 'C001',
      text: 'Street light flickering on Main Street',
      department: 'Electricity',
      urgency: 3,
      escalated: false,
      sentiment: 'neutral',
      date: '2024-12-23',
      status: 'Pending'
    }
  ];

  const handleSubmitResponse = () => {
    if (!response.trim()) return;
    alert('Response submitted successfully!');
    setResponse('');
    setSelectedComplaint(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-purple-100 p-8">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">Department Dashboard</h1>
              <p className="text-gray-600 mt-2">
                <span className="font-semibold">Department:</span> {user.department}
              </p>
            </div>
            <button
              onClick={onLogout}
              className="px-6 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Logout
            </button>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {/* Complaint Queue */}
            <div>
              <h2 className="text-xl font-bold text-gray-800 mb-4">Priority Queue</h2>
              <div className="space-y-3 max-h-[600px] overflow-y-auto">
                {complaints.map((complaint) => (
                  <div
                    key={complaint.id}
                    onClick={() => setSelectedComplaint(complaint)}
                    className={`border rounded-xl p-4 cursor-pointer transition-all ${
                      selectedComplaint?.id === complaint.id
                        ? 'border-indigo-500 bg-indigo-50'
                        : 'border-gray-200 hover:border-indigo-300 hover:shadow-md'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-semibold text-gray-600">
                          {complaint.id}
                        </span>
                        {complaint.escalated && (
                          <span className="px-2 py-1 bg-red-100 text-red-700 text-xs font-semibold rounded-full">
                            🚨 ESCALATED
                          </span>
                        )}
                      </div>
                      <span className="text-sm font-semibold text-indigo-600">
                        {complaint.urgency}/10
                      </span>
                    </div>
                    <p className="text-gray-800 text-sm mb-2 line-clamp-2">
                      {complaint.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-200 rounded-full h-2">
                        <div
                          className="bg-indigo-600 h-2 rounded-full"
                          style={{ width: `${complaint.urgency * 10}%` }}
                        />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Complaint Detail & Response */}
            <div>
              {selectedComplaint ? (
                <div className="border border-gray-200 rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h2 className="text-xl font-bold text-gray-800">Complaint Details</h2>
                    {selectedComplaint.escalated && (
                      <AlertTriangle className="text-red-600" size={24} />
                    )}
                  </div>

                  <div className="space-y-4 mb-6">
                    <div>
                      <span className="text-sm font-semibold text-gray-600">ID:</span>
                      <p className="text-gray-800">{selectedComplaint.id}</p>
                    </div>
                    <div>
                      <span className="text-sm font-semibold text-gray-600">Complaint:</span>
                      <p className="text-gray-800 mt-1">{selectedComplaint.text}</p>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <span className="text-sm font-semibold text-gray-600">Urgency:</span>
                        <p className="text-gray-800">{selectedComplaint.urgency}/10</p>
                      </div>
                      <div>
                        <span className="text-sm font-semibold text-gray-600">Sentiment:</span>
                        <p className="text-gray-800 capitalize">{selectedComplaint.sentiment}</p>
                      </div>
                    </div>
                    <div>
                      <span className="text-sm font-semibold text-gray-600">Date:</span>
                      <p className="text-gray-800">{selectedComplaint.date}</p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <label className="block text-sm font-semibold text-gray-700 mb-2">
                      Your Response
                    </label>
                    <textarea
                      value={response}
                      onChange={(e) => setResponse(e.target.value)}
                      placeholder="Enter your response to this complaint..."
                      rows={6}
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                    />
                    <button
                      onClick={handleSubmitResponse}
                      className="w-full mt-4 py-3 bg-indigo-600 text-white rounded-xl hover:bg-indigo-700 transition-colors font-semibold"
                    >
                      Submit Response
                    </button>
                  </div>
                </div>
              ) : (
                <div className="border border-dashed border-gray-300 rounded-xl p-12 text-center">
                  <p className="text-gray-500">Select a complaint to view details and respond</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;