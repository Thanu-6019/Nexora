// data.js

// -------------------- AI Features --------------------
const aiFeatures = [
  {
    title: "Smart Team Matching",
    description: "AI analyzes skills, interests, and past performance to create optimal team combinations.",
    icon: "🤖",
    color: "primary",
    activeText: "Active Learning"
  },
  {
    title: "Predictive Analytics",
    description: "Forecast attendance, engagement, and success metrics for better event planning.",
    icon: "📊",
    color: "accent",
    activeText: "Real-time Insights"
  },
  {
    title: "Personalized Recommendations",
    description: "Tailored event suggestions and networking opportunities based on user profiles.",
    icon: "🎯",
    color: "secondary",
    activeText: "Smart Matching"
  }
];

// Render AI Features
const aiContainer = document.getElementById("ai-features");
aiFeatures.forEach(feature => {
  aiContainer.innerHTML += `
    <div class="feature-card card-hover">
      <div class="feature-icon ${feature.color} flex items-center justify-center mb-4 text-xl">${feature.icon}</div>
      <h4 class="text-lg font-semibold mb-2">${feature.title}</h4>
      <p class="text-gray-600 mb-4">${feature.description}</p>
      <div class="flex items-center text-${feature.color} text-sm font-medium">
        <span class="ai-pulse mr-2">●</span>
        ${feature.activeText}
      </div>
    </div>
  `;
});

// -------------------- Quick Actions --------------------
const quickActions = [
  { title: "Quick Event Builder", description: "Drag-and-drop interface with AI suggestions", icon: "⚡", color: "primary" },
  { title: "VR/AR Events", description: "Immersive virtual experiences", icon: "🥽", color: "secondary" },
  { title: "Collaboration Hub", description: "Real-time chat, whiteboards, code editors", icon: "🤝", color: "accent" },
  { title: "Sustainability Tracker", description: "Carbon footprint calculator", icon: "🌱", color: "green" }
];

// Render Quick Actions
const quickContainer = document.getElementById("quick-actions");
quickActions.forEach(action => {
  quickContainer.innerHTML += `
    <div class="quick-action-card card-hover">
      <div class="quick-action-icon bg-${action.color}/10 flex items-center justify-center mb-4 text-lg">${action.icon}</div>
      <h4 class="font-semibold mb-2">${action.title}</h4>
      <p class="text-gray-600 text-sm">${action.description}</p>
    </div>
  `;
});

// -------------------- Recent Events --------------------
const recentEvents = [
  { name: "AI Hackathon 2024", date: "March 15-17", participants: 1247, status: "Live", initial: "H", statusClass: "status-live" },
  { name: "Tech Conference 2024", date: "April 2-4", participants: 856, status: "Upcoming", initial: "C", statusClass: "status-upcoming" },
  { name: "Web3 Summit", date: "May 10-12", participants: 432, status: "Upcoming", initial: "W", statusClass: "status-upcoming" },
  { name: "Design Sprint 2024", date: "June 5-7", participants: 210, status: "Live", initial: "D", statusClass: "status-live" }
];

// Render Recent Events
const eventsContainer = document.getElementById("recent-events");
recentEvents.forEach(event => {
  eventsContainer.innerHTML += `
    <div class="event-item flex items-center justify-between p-4 mb-2 bg-gray-50 rounded-lg">
      <div class="flex items-center space-x-4">
        <div class="event-avatar bg-primary flex items-center justify-center">${event.initial}</div>
        <div>
          <h4 class="font-semibold">${event.name}</h4>
          <p class="text-gray-600 text-sm">${event.date} • ${event.participants} participants</p>
        </div>
      </div>
      <div class="flex items-center space-x-2">
        <span class="status-badge ${event.statusClass}">${event.status}</span>
        <button class="text-primary hover:text-primary/80">Manage</button>
      </div>
    </div>
  `;
});

