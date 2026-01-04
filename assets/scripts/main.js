        const TILE_SIZE = 24;
        const PLAYER_SPEED = 2;   
        const GHOST_SPEED = 1.4;  

        const LEVEL_MAP = [
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
            [1,2,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,2,1],
            [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,0,1,1,9,1,1,0,1,0,1,1,0,1],
            [1,0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,1],
            [1,1,1,1,0,1,1,1,9,1,9,1,1,1,0,1,1,1,1],
            [1,9,9,9,0,1,9,9,9,9,9,9,9,1,0,9,9,9,1],
            [1,1,1,1,0,1,9,1,1,9,1,1,9,1,0,1,1,1,1],
            [1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1],
            [1,0,1,1,0,1,1,1,0,1,0,1,1,1,0,1,1,0,1],
            [1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1],
            [1,1,0,1,0,1,0,1,1,1,1,1,0,1,0,1,0,1,1],
            [1,2,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,2,1],
            [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1]
        ];

        class Game {
            constructor() {
                this.canvas = document.getElementById('gameCanvas');
                this.ctx = this.canvas.getContext('2d');
                
                this.cols = LEVEL_MAP[0].length;
                this.rows = LEVEL_MAP.length;
                this.canvas.width = this.cols * TILE_SIZE;
                this.canvas.height = this.rows * TILE_SIZE;

                this.walls = [];
                this.breads = [];
                this.powerUps = [];
                this.ghosts = [];
                
                this.player = {
                    x: 0, y: 0, 
                    dx: 0, dy: 0, 
                    nextDx: 0, nextDy: 0, 
                    angle: 0,
                    speed: PLAYER_SPEED
                };

                this.score = 0;
                this.lives = 3;
                this.level = 1;
                this.state = 'START';

                window.addEventListener('keydown', (e) => this.handleInput(e));
                this.loop();
            }

            startGame() {
                document.getElementById('start-screen').classList.add('hidden');
                document.getElementById('game-over-screen').classList.add('hidden');
                this.resetLevelData();
                this.state = 'PLAYING';
            }

            resetGame() {
                this.score = 0;
                this.level = 1;
                this.lives = 3;
                this.startGame();
            }

            resetLevelData() {
                this.walls = [];
                this.breads = [];
                this.powerUps = [];
                this.ghosts = [];

                for(let r=0; r<this.rows; r++){
                    for(let c=0; c<this.cols; c++){
                        let type = LEVEL_MAP[r][c];
                        if(type === 1) this.walls.push({x: c*TILE_SIZE, y: r*TILE_SIZE});
                        if(type === 0) this.breads.push({x: c*TILE_SIZE + 12, y: r*TILE_SIZE + 12, active: true});
                        if(type === 2) this.powerUps.push({x: c*TILE_SIZE + 12, y: r*TILE_SIZE + 12, active: true});
                    }
                }

                // Adicionar Donuts Extras (Transformando pães em donuts)
                for(let i=0; i<3; i++) {
                    if(this.breads.length > 0) {
                        let randomIndex = Math.floor(Math.random() * this.breads.length);
                        let target = this.breads[randomIndex];
                        this.powerUps.push({x: target.x, y: target.y, active: true});
                        this.breads.splice(randomIndex, 1);
                    }
                }

                // Spawn Player
                this.player.x = 9 * TILE_SIZE;
                this.player.y = 8 * TILE_SIZE;
                this.player.dx = 0; this.player.dy = 0;
                this.player.nextDx = 0; this.player.nextDy = 0;

                // Spawn Fantasmas
                this.ghosts.push({
                    x: 1 * TILE_SIZE, y: 1 * TILE_SIZE,
                    dx: 0, dy: 0,
                    color: '#ff0000',
                    speed: GHOST_SPEED
                });

                this.ghosts.push({
                    x: 16 * TILE_SIZE, y: 14 * TILE_SIZE,
                    dx: 0, dy: 0,
                    color: '#ffb852',
                    speed: GHOST_SPEED
                });

                this.ghosts.forEach(g => this.changeGhostDir(g));
                this.updateUI();
            }

            handleInput(e) {
                const code = e.code;

                if ((code === 'Space' || code === 'Enter') && this.state !== 'PLAYING') {
                    if (this.state === 'GAMEOVER') this.resetGame();
                    else this.startGame();
                    return;
                }

                // APENAS WASD
                if (code === 'KeyW') this.setDir(0, -1);
                if (code === 'KeyS') this.setDir(0, 1);
                if (code === 'KeyA') this.setDir(-1, 0);
                if (code === 'KeyD') this.setDir(1, 0);
            }

            setDir(dx, dy) {
                if(this.state !== 'PLAYING') return;
                this.player.nextDx = dx;
                this.player.nextDy = dy;
            }

            checkWallCollision(x, y, speed) {
                const margin = 6; 
                const size = TILE_SIZE - margin*2;
                const points = [
                    {x: x + margin, y: y + margin},
                    {x: x + margin + size, y: y + margin},
                    {x: x + margin, y: y + margin + size},
                    {x: x + margin + size, y: y + margin + size}
                ];

                for(let p of points) {
                    let c = Math.floor(p.x / TILE_SIZE);
                    let r = Math.floor(p.y / TILE_SIZE);
                    if(r >= 0 && r < this.rows && c >= 0 && c < this.cols) {
                        if(LEVEL_MAP[r][c] === 1) return true;
                    }
                }
                return false;
            }

            update() {
                if(this.state !== 'PLAYING') return;

                const p = this.player;
                
                // Movimento Fluid
                if (p.nextDx !== 0 || p.nextDy !== 0) {
                    if (!this.checkWallCollision(p.x + p.nextDx * p.speed, p.y + p.nextDy * p.speed, p.speed)) {
                        p.dx = p.nextDx;
                        p.dy = p.nextDy;
                    }
                }

                // Eixo X
                let nextX = p.x + p.dx * p.speed;
                if(!this.checkWallCollision(nextX, p.y, p.speed)) {
                    p.x = nextX;
                } else {
                    p.dx = 0; 
                }

                // Eixo Y
                let nextY = p.y + p.dy * p.speed;
                if(!this.checkWallCollision(p.x, nextY, p.speed)) {
                    p.y = nextY;
                } else {
                    p.dy = 0;
                }

                // Visual
                if(p.dx === 1) p.angle = 0;
                if(p.dx === -1) p.angle = Math.PI;
                if(p.dy === 1) p.angle = Math.PI/2;
                if(p.dy === -1) p.angle = -Math.PI/2;

                // Fantasmas
                this.ghosts.forEach(g => {
                    let nextGX = g.x + g.dx * g.speed;
                    let nextGY = g.y + g.dy * g.speed;

                    if(this.checkWallCollision(nextGX, nextGY, g.speed) || Math.random() < 0.015) {
                        this.changeGhostDir(g);
                    } else {
                        g.x = nextGX; g.y = nextGY;
                    }

                    if(Math.hypot((g.x+12) - (p.x+12), (g.y+12) - (p.y+12)) < TILE_SIZE - 4) {
                        this.handleDeath();
                    }
                });

                // Itens
                this.breads.forEach(b => {
                    if(b.active && Math.hypot(b.x - (p.x+12), b.y - (p.y+12)) < 10) {
                        b.active = false; this.score += 10; this.updateUI(); // Apenas pontos
                    }
                });

                this.powerUps.forEach(pu => {
                    if(pu.active && Math.hypot(pu.x - (p.x+12), pu.y - (p.y+12)) < 10) {
                        pu.active = false; this.score += 50; this.updateUI();
                        this.checkWin();
                    }
                });
            }

            changeGhostDir(g) {
                const dirs = [{x:0, y:-1}, {x:0, y:1}, {x:-1, y:0}, {x:1, y:0}];
                const validDirs = dirs.filter(d => !this.checkWallCollision(g.x + d.x*g.speed, g.y + d.y*g.speed, g.speed));

                if(validDirs.length > 0) {
                    if(Math.random() < 0.4) {
                        let best = validDirs[0];
                        let minDst = 9999;
                        validDirs.forEach(d => {
                            let dst = Math.hypot((g.x+d.x) - this.player.x, (g.y+d.y) - this.player.y);
                            if(dst < minDst) { minDst = dst; best = d; }
                        });
                        g.dx = best.x; g.dy = best.y;
                    } else {
                        let r = validDirs[Math.floor(Math.random() * validDirs.length)];
                        g.dx = r.x; g.dy = r.y;
                    }
                } else {
                    g.dx *= -1; g.dy *= -1;
                }
            }

            handleDeath() {
                this.lives--;
                this.updateUI();
                if(this.lives <= 0) {
                    this.state = 'GAMEOVER';
                    document.getElementById('final-score').innerText = this.score;
                    document.getElementById('game-over-screen').classList.remove('hidden');
                } else {
                    this.player.x = 9*TILE_SIZE; 
                    this.player.y = 8*TILE_SIZE;
                    this.player.dx = 0; this.player.dy = 0;
                    this.player.nextDx = 0; this.player.nextDy = 0;
                    this.ghosts[0].x = 1*TILE_SIZE; this.ghosts[0].y = 1*TILE_SIZE;
                    this.ghosts[1].x = 16*TILE_SIZE; this.ghosts[1].y = 14*TILE_SIZE;
                    this.ghosts.forEach(g => this.changeGhostDir(g));
                }
            }

            checkWin() {
                // ALTERADO: Agora verifica apenas os DONUTS
                if (this.powerUps.filter(p => p.active).length === 0) {
                    this.level++;
                    this.score += 100;
                    this.resetLevelData();
                }
            }

            draw() {
                this.ctx.fillStyle = '#0a0a12';
                this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

                this.ctx.fillStyle = '#141428';
                this.ctx.strokeStyle = '#2a2a50';
                this.ctx.lineWidth = 1;
                this.walls.forEach(w => {
                    this.ctx.fillRect(w.x, w.y, TILE_SIZE, TILE_SIZE);
                    this.ctx.strokeRect(w.x, w.y, TILE_SIZE, TILE_SIZE);
                });

                this.ctx.fillStyle = '#ffcc00';
                this.breads.forEach(b => {
                    if(b.active) this.ctx.fillRect(b.x-2, b.y-2, 4, 4);
                });

                this.powerUps.forEach(p => {
                    if(p.active) {
                        this.ctx.font = '14px Arial';
                        this.ctx.fillText('🍩', p.x-7, p.y+5);
                    }
                });

                this.ctx.save();
                this.ctx.translate(this.player.x + 12, this.player.y + 12);
                this.ctx.rotate(this.player.angle);
                this.ctx.fillStyle = '#ffcc00';
                this.ctx.shadowBlur = 10; this.ctx.shadowColor = '#ffcc00';
                this.ctx.beginPath();
                this.ctx.arc(0, 0, 10, 0.2 * Math.PI, 1.8 * Math.PI);
                this.ctx.lineTo(0,0);
                this.ctx.fill();
                this.ctx.restore();

                this.ghosts.forEach(g => {
                    this.ctx.fillStyle = g.color;
                    this.ctx.shadowBlur = 5; this.ctx.shadowColor = g.color;
                    this.ctx.beginPath();
                    this.ctx.arc(g.x+12, g.y+8, 10, Math.PI, 0);
                    this.ctx.lineTo(g.x+22, g.y+20);
                    this.ctx.lineTo(g.x+2, g.y+20);
                    this.ctx.fill();
                    this.ctx.fillStyle = '#fff';
                    this.ctx.shadowBlur = 0;
                    this.ctx.fillRect(g.x+7, g.y+6, 4, 4);
                    this.ctx.fillRect(g.x+13, g.y+6, 4, 4);
                });
            }

            updateUI() {
                document.getElementById('score-display').innerText = this.score;
                document.getElementById('level-display').innerText = this.level;
                document.getElementById('lives-display').innerText = '❤️'.repeat(this.lives);
            }

            loop() {
                this.update();
                this.draw();
                requestAnimationFrame(() => this.loop());
            }
        }

        const game = new Game();