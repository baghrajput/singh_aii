import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const API_BASE_URL = 'http://localhost:8000/api/v1'; // Assuming backend runs on port 8000

const Dashboard = () => {
  const [calls, setCalls] = useState([]);
  const [stats, setStats] = useState({
    sla_percentage: 'N/A',
    avg_latency_ms: 'N/A',
    sentiment_breakdown: { Positive: 0, Neutral: 0, Negative: 0 },
  });
  const [callVolumeData, setCallVolumeData] = useState([]);
  const [filterUrgency, setFilterUrgency] = useState('All');
  const [displayLanguage, setDisplayLanguage] = useState('English'); // 'English' or 'Arabic'

  const fetchDashboardData = async () => {
    try {
      // Fetch live calls
      const callsResponse = await fetch(`${API_BASE_URL}/dashboard/live-calls`);
      const liveCalls = await callsResponse.json();
      setCalls(liveCalls);

      // Fetch stats
      const statsResponse = await fetch(`${API_BASE_URL}/dashboard/stats`);
      const dashboardStats = await statsResponse.json();
      setStats(dashboardStats);

      // Fetch call volume
      const callVolumeResponse = await fetch(`${API_BASE_URL}/dashboard/call-volume`);
      const volumeData = await callVolumeResponse.json();
      setCallVolumeData(volumeData.map(item => ({ name: new Date(item.date).toLocaleDateString(), calls: item.count })));

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    }
  };

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 5000); // Auto-refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const filteredCalls = calls.filter(call => {
    if (filterUrgency === 'All') return true;
    return call.classification && call.classification.urgency === filterUrgency;
  });

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial', backgroundColor: '#f4f7f6', minHeight: '100vh' }}>
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', borderBottom: '2px solid #007cba', paddingBottom: '10px' }}>
        <h1 style={{ color: '#007cba' }}>Saudi Aramco AI Assistant - Supervisor Dashboard</h1>
        <div style={{ textAlign: 'right' }}>
          <strong>System Status:</strong> <span style={{ color: 'green' }}>Active</span>
          <div style={{ marginTop: '10px' }}>
            <button onClick={() => setDisplayLanguage('English')} style={{ marginRight: '5px', backgroundColor: displayLanguage === 'English' ? '#007cba' : '#ccc', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}>English</button>
            <button onClick={() => setDisplayLanguage('Arabic')} style={{ backgroundColor: displayLanguage === 'Arabic' ? '#007cba' : '#ccc', color: 'white', border: 'none', padding: '5px 10px', borderRadius: '4px', cursor: 'pointer' }}>العربية</button>
          </div>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px', marginTop: '20px' }}>
        <StatCard title="SLA Tracking" value={`${stats.sla_percentage}%`} color="#2ecc71" />
        <StatCard title="Avg Latency" value={`${stats.avg_latency_ms}ms`} color="#f1c40f" />
        <StatCard title="Overall Sentiment" value={Object.keys(stats.sentiment_breakdown).reduce((a, b) => stats.sentiment_breakdown[a] > stats.sentiment_breakdown[b] ? a : b, 'Neutral')} color="#3498db" />
      </div>

      <div style={{ marginTop: '30px', backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <h2>Call Volume (Last 7 Days)</h2>
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={callVolumeData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="calls" fill="#007cba" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div style={{ marginTop: '30px', backgroundColor: 'white', padding: '20px', borderRadius: '8px', boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
          <h2>Live Call Transcripts</h2>
          <div>
            <label htmlFor="urgency-filter" style={{ marginRight: '10px' }}>Filter by Urgency:</label>
            <select id="urgency-filter" value={filterUrgency} onChange={(e) => setFilterUrgency(e.target.value)} style={{ padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}>
              <option value="All">All</option>
              <option value="Emergency">Emergency</option>
              <option value="Urgent">Urgent</option>
              <option value="Non-Emergency">Non-Emergency</option>
            </select>
          </div>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ textAlign: 'left', borderBottom: '1px solid #eee' }}>
              <th style={{ padding: '10px' }}>Caller ID</th>
              <th>Transcript</th>
              <th>Intent</th>
              <th>Urgency</th>
              <th>Sentiment</th>
              <th>Action</th>
              <th>Timestamp</th>
            </tr>
          </thead>
          <tbody>
            {filteredCalls.map((call) => (
              <CallRow key={call.id} call={call} />
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, color }) => (
  <div style={{ backgroundColor: 'white', padding: '20px', borderRadius: '8px', borderLeft: `5px solid ${color}`, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
    <h4 style={{ margin: 0, color: '#666' }}>{title}</h4>
    <h2 style={{ margin: '10px 0 0 0' }}>{value}</h2>
  </div>
);

const CallRow = ({ call }) => (
  <tr style={{ borderBottom: '1px solid #eee' }}>
    <td style={{ padding: '10px' }}>{call.caller_id}</td>
    <td>{call.transcript}</td>
    <td><span style={{ backgroundColor: '#e1f5fe', padding: '2px 8px', borderRadius: '4px' }}>{call.classification ? call.classification.issue_type : 'N/A'}</span></td>
    <td><span style={{ color: call.classification && call.classification.urgency === 'Emergency' ? 'red' : (call.classification && call.classification.urgency === 'Urgent' ? 'orange' : 'green') }}>{call.classification ? call.classification.urgency : 'N/A'}</span></td>
    <td>{call.sentiment}</td>
    <td>{call.action_taken}</td>
    <td>{new Date(call.timestamp).toLocaleString()}</td>
  </tr>
);

export default Dashboard;
