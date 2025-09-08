const chartsData = {{CHARTS_DATA}};

// 搜索与排序
(function initSummaryTableHelpers() {
    const table = document.getElementById('summaryTable');
    if (!table) return;
    const input = document.getElementById('summarySearch');
    const clearBtn = document.getElementById('clearSearch');
    const hideUntimedSummaryRowsCheckbox = document.getElementById('hideUntimedSummaryRows'); // 新增

    function normalizeText(s) { return (s || '').toString().toLowerCase(); }

    function filterSummaryRows() {
        const q = normalizeText(input.value);
        const hideUntimed = hideUntimedSummaryRowsCheckbox ? hideUntimedSummaryRowsCheckbox.checked : false;
        const rows = table.tBodies[0].rows;

        for (let i = 0; i < rows.length; i++) {
            const row = rows[i];
            const cells = Array.from(row.cells).map(td => normalizeText(td.textContent));

            // 搜索过滤
            const searchOk = q === '' || cells.some(txt => txt.includes(q));

            // 隐藏无限时记录过滤 (针对 summaryTable)
            let untimedOk = true;
            if (hideUntimed) { // 如果选中，则隐藏无记录
                // 从第三个单元格开始（跳过玩家和角色名），检查是否有非"-"的层数记录
                const dungeonLevels = Array.from(row.cells).slice(2); // 获取副本层数单元格
                const hasTimedRun = dungeonLevels.some(cell => {
                    const levelText = cell.textContent.trim();
                    return levelText !== '-' && levelText !== '';
                });
                untimedOk = hasTimedRun; // 如果没有限时记录，则 untimedOk 为 false，隐藏
            }
            
            row.style.display = (searchOk && untimedOk) ? '' : 'none';
        }
    }

    if (input) input.addEventListener('input', filterSummaryRows);
    if (clearBtn) clearBtn.addEventListener('click', () => { input.value = ''; filterSummaryRows(); input.focus(); });
    if (hideUntimedSummaryRowsCheckbox) hideUntimedSummaryRowsCheckbox.addEventListener('change', filterSummaryRows); // 新增事件监听
    
    // 页面加载时立即执行一次过滤，以应用默认状态
    filterSummaryRows();

    function parseLevel(text) {
        if (!text || text === '-') return Number.NEGATIVE_INFINITY;
        const n = parseInt(text.replace('+', ''));
        return isNaN(n) ? Number.NEGATIVE_INFINITY : n;
    }
    function sortTable(colIndex, type, asc) {
        const tbody = table.tBodies[0];
        const rows = Array.from(tbody.rows).filter(r => r.style.display !== 'none');
        const getVal = (row) => {
            const txt = row.cells[colIndex]?.textContent?.trim() || '';
            if (type === 'level') return parseLevel(txt);
            if (!isNaN(parseFloat(txt)) && isFinite(txt)) return parseFloat(txt);
            return txt.toLowerCase();
        };
        rows.sort((a,b) => { const va=getVal(a), vb=getVal(b); if (va<vb) return asc?-1:1; if (va>vb) return asc?1:-1; return 0; });
        rows.forEach(r => tbody.appendChild(r));
    }
    const headCells = table.tHead.rows[0].cells;
    let sortState = {};
    Array.from(headCells).forEach((th, i) => {
        if (!th.classList.contains('sortable')) return;
        th.addEventListener('click', () => {
            const type = th.getAttribute('data-type') || 'text';
            const prev = sortState[i] || false;
            const nextAsc = !prev;
            sortState = { [i]: nextAsc };
            sortTable(i, type, nextAsc);
            Array.from(headCells).forEach(h => h.removeAttribute('data-sort'));
            th.setAttribute('data-sort', nextAsc ? 'asc' : 'desc');
        });
    });
})();

// 等级分布图
// 等级分布图
const levelCtx = document.getElementById('levelChart').getContext('2d');
const levelLabels = chartsData.level_distribution.labels;
const levelData = chartsData.level_distribution.data;
const layerColorMap = chartsData.LAYER_COLOR_MAP;

// 根据层数获取颜色
const levelBackgroundColors = levelLabels.map(label => {
    const level = parseInt(label.replace('+', ''));
    return `#${layerColorMap[level] || '888888'}`; // 默认灰色
});
const levelBorderColors = levelBackgroundColors.map(color => color); // 边框颜色与背景色相同

new Chart(levelCtx, {
    type: 'bar',
    data: {
        labels: levelLabels,
        datasets: [{
            label: '数量',
            data: levelData,
            backgroundColor: levelBackgroundColors,
            borderColor: levelBorderColors,
            borderWidth: 1
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    stepSize: 1,
                    font: {
                        size: 16 // 增大Y轴字体
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 16 // 增大X轴字体
                    }
                }
            }
        }
    }
});

// 副本表现图 (组合图：柱状图为平均等级，折线图为限时率)
const dungeonCtx = document.getElementById('dungeonChart').getContext('2d');
const dungeonLabels = chartsData.dungeon_performance.labels; // 简称
const dungeonFullNames = chartsData.dungeon_performance.full_names; // 全称
const dungeonAvgLevels = chartsData.dungeon_performance.avg_levels;
const dungeonTimedRates = chartsData.dungeon_performance.timed_rates;
const dungeonColorMap = chartsData.DUNGEON_COLOR_MAP;

// 根据副本全称获取颜色
const dungeonBackgroundColors = dungeonFullNames.map(fullName => {
    return dungeonColorMap[fullName] || 'rgba(120, 120, 120, 0.8)'; // 默认灰色
});
const dungeonBorderColors = dungeonBackgroundColors.map(color => color.replace('0.8)', '1)')); // 边框颜色使用不透明版本

new Chart(dungeonCtx, {
    type: 'bar', // 主类型为柱状图
    data: {
        labels: dungeonLabels,
        datasets: [{
            type: 'bar', // 平均等级 - 柱状图
            label: '平均等级',
            data: dungeonAvgLevels,
            backgroundColor: dungeonBackgroundColors,
            borderColor: dungeonBorderColors,
            borderWidth: 1,
            yAxisID: 'y-avg-level'
        }, {
            type: 'line', // 通关率 - 折线图
            label: '通关率 (%)',
            data: dungeonTimedRates,
            fill: false,
            borderColor: 'rgba(255, 99, 132, 1)', // 使用一个鲜明的红色作为折线颜色
            tension: 0.1,
            yAxisID: 'y-completion-rate'
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    font: {
                        size: 16 // 增大图例字体
                    }
                }
            },
            tooltip: {
                mode: 'index',
                intersect: false,
                titleFont: {
                    size: 16 // 增大tooltip标题字体
                },
                bodyFont: {
                    size: 16 // 增大tooltip内容字体
                },
                callbacks: {
                    title: function(tooltipItems) {
                        // 获取当前副本的简称
                        const shortName = tooltipItems[0].label;
                        // 从 chartsData 中获取全称映射
                        const fullNameMap = chartsData.DUNGEON_FULL_NAME_MAP;
                        // 查找全称
                        const fullName = fullNameMap[shortName] || shortName;
                        return fullName; // 显示全称
                    },
                    label: function(tooltipItem) {
                        let label = tooltipItem.dataset.label || '';
                        if (label) {
                            label += ': ';
                        }
                        if (tooltipItem.parsed.y !== null) {
                            label += tooltipItem.parsed.y;
                        }
                        return label;
                    }
                }
            }
        },
        scales: {
            'y-avg-level': {
                type: 'linear',
                position: 'left',
                beginAtZero: true,
                title: {
                    display: true,
                    text: '平均等级',
                    font: {
                        size: 16 // 增大Y轴标题字体
                    }
                },
                ticks: {
                    font: {
                        size: 16 // 增大Y轴刻度字体
                    }
                }
            },
            'y-completion-rate': {
                type: 'linear',
                position: 'right',
                beginAtZero: true,
                max: 100,
                title: {
                    display: true,
                    text: '通关率 (%)',
                    font: {
                        size: 16 // 增大Y轴标题字体
                    }
                },
                ticks: {
                    font: {
                        size: 16 // 增大Y轴刻度字体
                    },
                },
                grid: {
                    drawOnChartArea: false, // 只绘制左侧Y轴的网格线
                },
            },
            x: {
                ticks: {
                    font: {
                        size: 16 // 增大X轴刻度字体
                    }
                }
            }
        }
    }
});

// 职业平均层数图
const classCtx = document.getElementById('classChart').getContext('2d');
const classLabels = Object.keys(chartsData.class_performance);
const classLevels = classLabels.map(c => chartsData.class_performance[c].avg_level);
const classColors = classLabels.map(c => chartsData.class_performance[c].color || 'rgba(120,120,120,0.8)');

new Chart(classCtx, {
    type: 'bar',
    data: {
        labels: classLabels,
        datasets: [{
            label: '平均层数',
            data: classLevels,
            backgroundColor: classColors,
        }]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { display: false } },
        scales: {
            y: {
                beginAtZero: true,
                ticks: {
                    font: {
                        size: 16 // 增大Y轴字体
                    }
                }
            },
            x: {
                ticks: {
                    font: {
                        size: 16 // 增大X轴字体
                    }
                }
            }
        }
    }
});

// 角色统计动态渲染、排序和过滤
(function initCharacterStats() {
    const characterStatsData = chartsData.character_stats_data;
    const characterStatsContainer = document.getElementById('characterStatsCards');
    const hideEmptyCharsCheckbox = document.getElementById('hideEmptyChars');
    const characterSortBySelect = document.getElementById('characterSortBy');

    function renderCharacterStats(data) {
        console.log("Rendering character stats with data:", data);
        characterStatsContainer.innerHTML = ''; // 清空现有卡片
        if (data.length === 0) {
            characterStatsContainer.innerHTML = '<p style="text-align: center; width: 100%; color: #7f8c8d;">没有符合条件的记录。</p>';
            return;
        }
        data.forEach(stat => {
            const classColor = chartsData.CLASS_COLOR_MAP[stat.class] || '888888'; // 从chartsData获取颜色，默认灰色
            const cardHtml = `
                <div class="stat-card">
                    <div class="card-header" style="border-left-color: #${classColor};">
                        <div class="character-info">
                            <div class="character-name">${stat.character}</div>
                            <div class="character-server">${stat.server}</div>
                        </div>
                        <div class="character-class ${'class-' + stat.class}" style="color: #${classColor};">${stat.class}</div>
                    </div>
                    <div class="card-content">
                        <div class="stat-item">
                            <span class="stat-label">平均等级</span>
                            <span class="stat-value">${typeof stat.avg_level === 'number' ? stat.avg_level.toFixed(2) : 'N/A'}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">通关率</span>
                            <span class="stat-value">${typeof stat.completion_rate === 'number' ? stat.completion_rate.toFixed(2) : 'N/A'}%</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">限时完成</span>
                            <span class="stat-value">${stat.timed_runs}/${stat.total_runs}</span>
                        </div>
                    </div>
                </div>
            `;
            characterStatsContainer.insertAdjacentHTML('beforeend', cardHtml);
        });
    }

    function applyFiltersAndSort() {
        let filteredData = [...characterStatsData];
        console.log("Original characterStatsData:", characterStatsData);

        // 过滤
        if (hideEmptyCharsCheckbox.checked) {
            filteredData = filteredData.filter(char => {
                // 隐藏无记录角色：total_runs 为 0，或者 avg_level 为 0/NaN
                const hasMeaningfulRecords = (!isNaN(char.total_runs) && char.total_runs > 0) &&
                                             (!isNaN(char.avg_level) && char.avg_level > 0);
                console.log(`Filtering ${char.character}: total_runs=${char.total_runs}, avg_level=${char.avg_level}, hasMeaningfulRecords=${hasMeaningfulRecords}`);
                return hasMeaningfulRecords;
            });
            console.log("Filtered data (hide empty):", filteredData);
        }

        // 排序
        const sortBy = characterSortBySelect.value;
        filteredData.sort((a, b) => {
            switch (sortBy) {
                case 'avg_level_desc': return b.avg_level - a.avg_level;
                case 'avg_level_asc': return a.avg_level - b.avg_level;
                case 'completion_rate_desc': return b.completion_rate - a.completion_rate;
                case 'completion_rate_asc': return a.completion_rate - b.completion_rate;
                case 'class_asc': return a.class.localeCompare(b.class);
                case 'class_desc': return b.class.localeCompare(a.class);
                case 'character_name_asc': return a.character.localeCompare(b.character);
                case 'character_name_desc': return b.character.localeCompare(a.character);
                default: return 0;
            }
        });
        console.log("Sorted data:", filteredData);

        renderCharacterStats(filteredData);
    }

    // 添加事件监听器
    hideEmptyCharsCheckbox.addEventListener('change', applyFiltersAndSort);
    characterSortBySelect.addEventListener('change', applyFiltersAndSort);

    // 初始渲染
    applyFiltersAndSort();
})();

// 玩家统计图表
(function initPlayerChart() {
    const playerCtx = document.getElementById('playerChart').getContext('2d');
    const playerChartData = chartsData.player_stats_data; // 现在 player_stats_data 包含 player_labels 和 datasets

    if (!playerChartData || !playerChartData.player_labels || playerChartData.player_labels.length === 0) {
        playerCtx.canvas.parentNode.innerHTML = '<p style="text-align: center; color: #7f8c8d;">暂无玩家统计数据。</p>';
        return;
    }

    // 找到最牛逼的玩家（平均等级最高） - 需要重新计算，因为数据结构变了
    // 假设 playerChartData.player_labels 已经按平均等级降序排序
    const playerLabels = playerChartData.player_labels;
    const datasets = playerChartData.datasets;

    // 计算每个玩家的总平均等级，用于皇冠标记
    const playerOverallAvgLevels = playerLabels.map((player, playerIndex) => {
        let totalLevelSum = 0;
        let totalRuns = 0;
        datasets.forEach(dataset => {
            const dungeonAvgLevel = dataset.meta.avg_levels[playerIndex];
            const dungeonRuns = dataset.meta.runs[playerIndex];
            if (dungeonRuns > 0) {
                totalLevelSum += dungeonAvgLevel * dungeonRuns;
                totalRuns += dungeonRuns;
            }
        });
        return totalRuns > 0 ? totalLevelSum / totalRuns : 0;
    });

    let bestPlayerIndex = -1;
    let maxAvgLevel = -1;
    playerOverallAvgLevels.forEach((avgLevel, index) => {
        if (avgLevel > maxAvgLevel) {
            maxAvgLevel = avgLevel;
            bestPlayerIndex = index;
        }
    });

    const finalPlayerLabels = playerLabels.map((label, index) => {
        if (index === bestPlayerIndex) {
            // 使用更大的皇冠emoji，并调整字体大小
            return '👑 ' + label; // 保持原样，因为Chart.js的label不支持HTML，直接改emoji字符
        }
        return label;
    });

    // 调整皇冠emoji的大小，通过修改y轴ticks的字体大小来影响
    // 由于Chart.js的label是绘制在canvas上的，不能直接用CSS控制emoji大小
    // 只能通过调整整个label的字体大小来间接影响
    // 考虑到用户要求“很大”，我们将y轴ticks的字体大小进一步增大
    const playerLabelFontSize = 18; // 进一步增大字体大小
    const playerLabelFontWeight = 'bold'; // 保持加粗

    const playerChartInstance = new Chart(playerCtx, {
        type: 'bar', // 堆叠柱状图
        data: {
            labels: finalPlayerLabels,
            datasets: datasets
        },
        options: {
            indexAxis: 'y', // 横向柱状图
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true, // 显示图例，因为有多个数据集（副本）
                    position: 'top',
                    labels: {
                        font: {
                            size: 14 // 增大副本名字字体
                        }
                    }
                },
                tooltip: {
                    enabled: false // 禁用tooltip
                }
            },
            scales: {
                x: {
                    stacked: true, // X轴堆叠
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '平均等级贡献'
                    }
                },
                y: {
                    stacked: true, // Y轴堆叠
                    title: {
                        display: false, // 删除Y轴标题
                        text: '玩家'
                    },
                    ticks: {
                        font: {
                            size: playerLabelFontSize, // 增大玩家名字字体
                            weight: playerLabelFontWeight // 加粗
                        }
                    },
                    barPercentage: 1.0, // 移除柱状条间隔
                    categoryPercentage: 1.0, // 移除柱状条间隔
                    // 尝试设置barThickness为'flex'，让Chart.js自动计算最佳宽度
                    barThickness: 'flex',
                    grid: {
                        offset: false // 确保网格线不偏移，可能影响柱子位置
                    }
                }
            },
            onClick: (e) => {
                const activePoints = playerChartInstance.getElementsAtEventForMode(e, 'nearest', { intersect: true }, true);
                if (activePoints.length > 0) {
                    const clickedDatasetIndex = activePoints[0].datasetIndex;
                    const clickedElementIndex = activePoints[0].index;
                    const playerName = playerChartInstance.data.labels[clickedElementIndex].replace('👑 ', ''); // 移除皇冠emoji

                    showPlayerDetailModal(playerName);
                }
            }
        }
    });
})();

// 玩家详情弹窗逻辑
let playerDetailChartInstance = null; // 用于存储弹窗图表实例

function showPlayerDetailModal(playerName) {
    const modal = document.getElementById('playerDetailModal');
    const modalTitle = document.getElementById('modalTitle');
    const playerDetailChartCanvas = document.getElementById('playerDetailChart');
    const closeButton = document.querySelector('#playerDetailModal .close-button');

    modalTitle.textContent = `${playerName} 的角色副本统计`;
    modal.style.display = 'flex'; // Show the modal

    // 获取玩家的详细角色数据
    const playerCharactersData = chartsData.player_character_dungeon_stats[playerName];

    if (!playerCharactersData || playerCharactersData.length === 0) {
        playerDetailChartCanvas.parentNode.innerHTML = '<p style="text-align: center; color: #7f8c8d;">没有找到该玩家的角色副本数据。</p>';
        return;
    }

    // 聚合所有角色的副本数据
    const aggregatedDungeonStats = {}; // {dungeonName: {total_level_sum: X, total_runs: Y}}

    playerCharactersData.forEach(char => {
        for (const dungeonName in char.dungeon_stats) {
            const stats = char.dungeon_stats[dungeonName];
            if (!aggregatedDungeonStats[dungeonName]) {
                aggregatedDungeonStats[dungeonName] = { level_sum: 0, runs: 0 };
            }
            aggregatedDungeonStats[dungeonName].level_sum += (stats.avg_level * stats.total_runs);
            aggregatedDungeonStats[dungeonName].runs += stats.total_runs;
        }
    });

    // 准备 Chart.js 数据
    const dungeonLabels = [];
    const avgLevels = [];
    const backgroundColors = [];
    const borderColors = [];

    // 按照 DUNGEON_NAME_MAP 的顺序来显示副本，确保一致性
    const allDungeons = Object.values(chartsData.DUNGEON_FULL_NAME_MAP); // 获取所有副本全称

    allDungeons.forEach(dungeonFullName => {
        if (aggregatedDungeonStats[dungeonFullName] && aggregatedDungeonStats[dungeonFullName].runs > 0) {
            const avgLevel = aggregatedDungeonStats[dungeonFullName].level_sum / aggregatedDungeonStats[dungeonFullName].runs;
            const dungeonShortName = chartsData.DUNGEON_SHORT_NAME_MAP[dungeonFullName] || dungeonFullName; // 获取简称
            dungeonLabels.push(dungeonShortName); // 使用简称
            avgLevels.push(avgLevel.toFixed(1)); // 保留一位小数

            const color = chartsData.DUNGEON_COLOR_MAP[dungeonFullName] || 'rgba(120, 120, 120, 0.8)';
            backgroundColors.push(color);
            borderColors.push(color.replace('0.8)', '1)'));
        }
    });

    // 如果没有数据，显示提示
    if (dungeonLabels.length === 0) {
        playerDetailChartCanvas.parentNode.innerHTML = '<p style="text-align: center; color: #7f8c8d;">该玩家没有有效的副本记录。</p>';
        return;
    }

    // 销毁旧图表实例（如果存在）
    if (playerDetailChartInstance) {
        playerDetailChartInstance.destroy();
    }

    // 创建新图表
    playerDetailChartInstance = new Chart(playerDetailChartCanvas, {
        type: 'bar',
        data: {
            labels: dungeonLabels,
            datasets: [{
                label: '平均层数',
                data: avgLevels,
                backgroundColor: backgroundColors,
                borderColor: borderColors,
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        title: function(tooltipItems) {
                            return tooltipItems[0].label; // 显示副本全称
                        },
                        label: function(tooltipItem) {
                            return `平均层数: ${tooltipItem.parsed.y}`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: '平均层数'
                    },
                    ticks: {
                        stepSize: 1
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: '副本'
                    }
                }
            }
        }
    });

    // 关闭弹窗事件监听
    closeButton.onclick = function() {
        modal.style.display = 'none';
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = 'none';
        }
    }
}

// AFK Player Logic
(function initAfkPlayerLogic() {
    const afkIcon = document.getElementById('afk-icon'); // Keep this for now, might be useful for other things
    const afkIconContainer = document.querySelector('.afk-icon-container'); // Get the container
    const afkPlayerModal = document.getElementById('afkPlayerModal');
    const afkCloseButton = document.getElementById('afkCloseButton');
    const afkPlayerListContainer = document.getElementById('afkPlayerList');
    const loveProgressBar = document.getElementById('loveProgressBar');
    const loveCountSpan = document.getElementById('loveCount');
    const emojiRainContainer = document.getElementById('emojiRainContainer');

    let afkPlayers = []; // Store identified AFK players as objects: {name: 'PlayerName', clicks: 0}
    let totalLoveProgress = 0; // Total clicks across all players
    let maxTotalLoveProgress = 0; // Max possible clicks (num_afk_players * 10)
    const MAX_CLICKS_PER_PLAYER = 10; // Each player needs 10 clicks
    let emojiRainActive = false; // Flag to track if emoji rain is active
    let emojiRainTimeoutId; // New variable to store the timeout ID for stopping rain

    // Function to identify AFK players
    function identifyAfkPlayers() {
        const allPlayers = {}; // {playerName: {total_runs: X, characters: [{...}]}}

        // Aggregate character data by player
        chartsData.character_stats_data.forEach(char => {
            if (!allPlayers[char.player]) {
                allPlayers[char.player] = {
                    total_runs: 0,
                    characters: []
                };
            }
            allPlayers[char.player].total_runs += char.total_runs;
            allPlayers[char.player].characters.push(char);
        });

        const identifiedAfkPlayers = [];
        for (const playerName in allPlayers) {
            const playerData = allPlayers[playerName];
            // An AFK player is one whose all characters have 0 total_runs
            if (playerData.total_runs === 0) {
                identifiedAfkPlayers.push({ name: playerName, clicks: 0 }); // Store as object with clicks
            }
        }
        return identifiedAfkPlayers;
    }

    // Function to render AFK players in the modal
    function renderAfkPlayers() {
        afkPlayerListContainer.innerHTML = ''; // Clear previous list
        if (afkPlayers.length === 0) {
            afkPlayerListContainer.innerHTML = '<p>恭喜！所有玩家都在线！</p>';
            return;
        }

        afkPlayers.forEach(player => {
            const playerDiv = document.createElement('div');
            playerDiv.classList.add('afk-player-item'); // Use a new class for styling
            playerDiv.dataset.playerName = player.name; // Store player name for click handling

            const playerNameSpan = document.createElement('span');
            playerNameSpan.classList.add('afk-player-name');
            playerNameSpan.textContent = player.name;

            const playerProgressBarContainer = document.createElement('div');
            playerProgressBarContainer.classList.add('player-progress-bar-container');
            const playerProgressBar = document.createElement('div');
            playerProgressBar.classList.add('player-progress-bar');
            playerProgressBar.style.width = `${(player.clicks / MAX_CLICKS_PER_PLAYER) * 100}%`;
            playerProgressBarContainer.appendChild(playerProgressBar);

            const playerClicksSpan = document.createElement('span');
            playerClicksSpan.classList.add('player-clicks-count');
            playerClicksSpan.textContent = `${player.clicks}/${MAX_CLICKS_PER_PLAYER}`;

            playerDiv.appendChild(playerNameSpan);
            playerDiv.appendChild(playerProgressBarContainer);
            playerDiv.appendChild(playerClicksSpan);

            playerDiv.addEventListener('click', (event) => {
                handlePlayerClick(event, player.name); // Pass player name to handler
            });
            afkPlayerListContainer.appendChild(playerDiv);
        });
    }

    // Handle player name click
    function handlePlayerClick(event, clickedPlayerName) {
        const player = afkPlayers.find(p => p.name === clickedPlayerName);
        if (!player || player.clicks >= MAX_CLICKS_PER_PLAYER) {
            return; // Player not found or already maxed out
        }

        const x = event.clientX;
        const y = event.clientY;

        // Create and animate the emoji
        const emoji = document.createElement('span');
        emoji.classList.add('emoji-fade-out');
        emoji.textContent = '💋'; // Kiss emoji
        emoji.style.left = `${x - 20}px`; // Adjust position to center emoji
        emoji.style.top = `${y - 20}px`;
        document.body.appendChild(emoji);

        emoji.addEventListener('animationend', () => {
            emoji.remove();
        });

        // Update individual player's love progress
        player.clicks++;
        totalLoveProgress = afkPlayers.reduce((sum, p) => sum + p.clicks, 0); // Recalculate total progress

        // Update individual player's UI
        const playerDiv = afkPlayerListContainer.querySelector(`[data-player-name="${player.name}"]`);
        if (playerDiv) {
            const playerProgressBar = playerDiv.querySelector('.player-progress-bar');
            const playerClicksSpan = playerDiv.querySelector('.player-clicks-count');
            playerProgressBar.style.width = `${(player.clicks / MAX_CLICKS_PER_PLAYER) * 100}%`;
            playerClicksSpan.textContent = `${player.clicks}/${MAX_CLICKS_PER_PLAYER}`;
        }

        // Update overall love progress bar
        loveProgressBar.style.width = `${(totalLoveProgress / maxTotalLoveProgress) * 100}%`;
        loveCountSpan.textContent = `${totalLoveProgress}/${maxTotalLoveProgress}`;

        if (totalLoveProgress >= maxTotalLoveProgress && !emojiRainActive) {
            startEmojiRain();
            // Optionally disable further clicks until rain stops or modal closes
            afkPlayerListContainer.querySelectorAll('.afk-player-item').forEach(el => el.style.pointerEvents = 'none');
        }
    }

    // Start emoji rain effect
    let emojiRainInterval;
    function startEmojiRain() {
        emojiRainActive = true;
        const emojis = ['💖', '✨', '🌟', '🌈', '💕', '💞', '💓', '💗', '💘', '💝']; // Emojis to fall
        let duration = 5000; // 5 seconds
        let startTime = Date.now();

        // Clear any existing rain
        stopEmojiRain(); // This call is correct to prevent multiple rains

        emojiRainInterval = setInterval(() => {
            // This condition is inside setInterval, meaning it checks every 100ms
            if (Date.now() - startTime > duration) {
                stopEmojiRain(); // If this condition is met, it stops the *current* rain.
                return;
            }
            const emoji = document.createElement('span');
            emoji.classList.add('falling-emoji');
            emoji.textContent = emojis[Math.floor(Math.random() * emojis.length)];
            emoji.style.left = `${Math.random() * 100}vw`;
            emoji.style.animationDuration = `${Math.random() * 2 + 3}s`; // 3-5 seconds
            emoji.style.animationDelay = `${Math.random() * 0.5}s`;
            emojiRainContainer.appendChild(emoji);

            emoji.addEventListener('animationend', () => {
                emoji.remove();
            });
        }, 100);

        // Set a timeout to stop the rain after the specified duration
        emojiRainTimeoutId = setTimeout(() => {
            stopEmojiRain();
        }, duration);
    }

    function stopEmojiRain() {
        clearInterval(emojiRainInterval);
        clearTimeout(emojiRainTimeoutId); // Clear the timeout as well
        emojiRainContainer.innerHTML = ''; // Clear all falling emojis
        emojiRainActive = false;
        afkPlayerListContainer.querySelectorAll('.afk-player-name').forEach(el => el.style.pointerEvents = 'auto');
    }

    // Event listeners
    if (afkIconContainer) {
        afkIconContainer.addEventListener('click', () => {
            afkPlayers = identifyAfkPlayers();
            maxTotalLoveProgress = afkPlayers.length * MAX_CLICKS_PER_PLAYER; // Calculate max total progress
            totalLoveProgress = afkPlayers.reduce((sum, p) => sum + p.clicks, 0); // Initialize total progress

            renderAfkPlayers();
            afkPlayerModal.style.display = 'flex';
            
            // Update overall progress bar on open
            loveProgressBar.style.width = `${(totalLoveProgress / maxTotalLoveProgress) * 100}%`;
            loveCountSpan.textContent = `${totalLoveProgress}/${maxTotalLoveProgress}`;
        });
    }

    if (afkCloseButton) {
        afkCloseButton.addEventListener('click', () => {
            afkPlayerModal.style.display = 'none';
            // Do NOT reset progress on close, keep it for next open
            // Do NOT stop emoji rain here
        });
    }

    // Close modal when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === afkPlayerModal) {
            afkPlayerModal.style.display = 'none';
            // Do NOT reset progress on close, keep it for next open
            // Do NOT stop emoji rain here
        }
    });
})();
