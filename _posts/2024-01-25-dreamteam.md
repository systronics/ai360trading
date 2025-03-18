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
    <!-- ... (keep HTML structure the same) ... -->

    <script>
        function addPlayer() {
            const newRow = document.querySelector('.input-row').cloneNode(true);
            newRow.querySelectorAll('input').forEach(input => input.value = '');
            document.getElementById('players-container').appendChild(newRow);
        }

        function shuffle(array) {
            for (let i = array.length - 1; i > 0; i--) {
                const j = Math.floor(Math.random() * (i + 1));
                [array[i], array[j]] = [array[j], array[i]];
            }
            return array;
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

            const CREDIT_LIMIT = 100;
            const REQUIRED_ROLES = {
                'Batsman': 3,
                'Bowler': 3,
                'Wicketkeeper': 1,
                'All-Rounder': 1
            };
            
            let allTeams = [];
            let attempts = 0;
            const MAX_ATTEMPTS = 1000;

            while (allTeams.length < 20 && attempts < MAX_ATTEMPTS) {
                attempts++;
                let team = [];
                let credits = 0;
                const shuffled = shuffle([...players]);
                
                // Select 11 players within credit limit
                for (const player of shuffled) {
                    if (team.length >= 11) break;
                    if (credits + player.credit <= CREDIT_LIMIT) {
                        team.push(player);
                        credits += player.credit;
                    }
                }

                // Check if team is valid
                if (team.length === 11 && credits <= CREDIT_LIMIT) {
                    // Check role requirements
                    const roleCounts = team.reduce((acc, p) => {
                        acc[p.role] = (acc[p.role] || 0) + 1;
                        return acc;
                    }, {});

                    const isValid = Object.entries(REQUIRED_ROLES).every(([role, min]) => 
                        (roleCounts[role] || 0) >= min
                    );

                    if (isValid) {
                        // Check for duplicate teams
                        const signature = team.map(p => p.name).sort().join(',');
                        const isUnique = !allTeams.some(t => t.signature === signature);

                        if (isUnique) {
                            // Select captain and vice-captain
                            const sorted = [...team].sort((a, b) => b.points - a.points);
                            const captain = sorted[0];
                            const vice = sorted.slice(1).find(p => p.role !== captain.role) || sorted[1];
                            
                            allTeams.push({
                                players: sorted,
                                captain: captain.name,
                                viceCaptain: vice.name,
                                totalCredit: credits.toFixed(1),
                                signature: signature
                            });
                        }
                    }
                }
            }

            if (allTeams.length < 20) {
                alert(`Generated ${allTeams.length} teams (max attempts reached)`);
            }

            displayTeams(allTeams);
        }

        function displayTeams(teams) {
            const resultsDiv = document.getElementById('results');
            resultsDiv.innerHTML = '';
            teams.forEach((team, index) => {
                const teamDiv = document.createElement('div');
                teamDiv.className = 'team-box';
                teamDiv.innerHTML = `
                    <b>Team ${index + 1}</b> (Credit: ${team.totalCredit})<br>
                    Captain: ${team.captain}<br>
                    Vice-Captain: ${team.viceCaptain}<br>
                    ${team.players.map(p => `
                        <div class="player-line">
                            <span>${p.name}</span>
                            <span>${p.role}</span>
                        </div>
                    `).join('')}
                `;
                resultsDiv.appendChild(teamDiv);
            });
        }
    </script>
</body>
