---
layout:           post
title:            Dream 11 Team Generator
date:             2025-02-25T13:04:19+05:45
last_modified_at: 2025-02-25T05:20:00+05:45
image:            https://ai360trading.in/public/image/logo.webp
excerpt:          Dream11, Dream Team, Dream Team ai 
tags:             free-ai-tools
---

    
<body>
    <div class="container">
        <h3 style="margin:5px 0">Team Generator</h3>
        
        <button id="add-player-btn" onclick="addPlayer()">+ Add Player</button>
        
        <div id="players-container">
            <div class="input-row">
                <input type="text" placeholder="Name" class="name">
                <select class="role">
                    <option value="Batsman">Batsman</option>
                    <option value="Bowler">Bowler</option>
                    <option value="All-Rounder">All-Rounder</option>
                    <option value="Wicketkeeper">Wicketkeeper</option>
                </select>
                <input type="number" placeholder="Points" class="points" min="0">
                <input type="number" placeholder="Credit" class="credit" min="1" max="12" step="0.5">
            </div>
        </div>

        <button onclick="generateTeams()">Generate 20 Teams</button>
        <div id="results" class="teams-grid"></div>
    </div>

    <script>
        function addPlayer() {
            const newRow = document.querySelector('.input-row').cloneNode(true);
            newRow.querySelectorAll('input').forEach(input => input.value = '');
            document.getElementById('players-container').appendChild(newRow);
        }

        function generateTeams() {
            const players = Array.from(document.querySelectorAll('.input-row')).map(row => ({
                name: row.querySelector('.name').value,
                role: row.querySelector('.role').value,
                points: parseFloat(row.querySelector('.points').value),
                credit: parseFloat(row.querySelector('.credit').value)
            })).filter(p => p.name && !isNaN(p.points) && !isNaN(p.credit));

            if (players.length < 11) {
                alert('Minimum 11 players required!');
                return;
            }

            let allTeams = [];
            for (let i = 0; i < 20; i++) {
                const shuffled = shuffle([...players]);
                const team = shuffled.slice(0, Math.ceil(shuffled.length/2));
                const sortedTeam = team.sort((a, b) => b.points - a.points);
                const captain = sortedTeam[0];
                const vice = sortedTeam.find(p => p.role !== captain.role) || sortedTeam[1];
                
                allTeams.push({
                    players: sortedTeam,
                    captain: captain.name,
                    viceCaptain: vice.name,
                    totalCredit: sortedTeam.reduce((sum, p) => sum + p.credit, 0).toFixed(1)
                });
            }

            displayTeams(allTeams);
        }

        // Rest of the JavaScript functions remain same
        // ... [Keep the shuffle(), displayTeams() functions from previous code]
    </script>
</body>
