from typing import Dict, List, Optional
from semantic_kernel.functions import kernel_function


class PhaserToolsPlugin:
    """Plugin providing Phaser 3 game development tools and templates"""
    
    @kernel_function(
        name="get_game_template",
        description="Get a basic Phaser 3 game template"
    )
    async def get_game_template(
        self,
        game_type: str = "basic"
    ) -> Dict[str, str]:
        """Get a Phaser 3 game template based on the game type"""
        templates = {
            "basic": self._get_basic_template(),
            "platformer": self._get_platformer_template(),
            "shooter": self._get_shooter_template(),
            "puzzle": self._get_puzzle_template(),
            "arcade": self._get_arcade_template()
        }
        
        template = templates.get(game_type.lower(), templates["basic"])
        
        return {
            "status": "success",
            "game_type": game_type,
            "template": template,
            "description": f"Phaser 3 {game_type} game template"
        }
    
    @kernel_function(
        name="get_phaser_config",
        description="Get Phaser 3 game configuration options"
    )
    async def get_phaser_config(
        self,
        width: int = 800,
        height: int = 600,
        physics_type: str = "arcade",
        responsive: bool = True
    ) -> Dict[str, any]:
        """Generate a Phaser 3 game configuration"""
        config = {
            "type": "Phaser.AUTO",
            "width": width,
            "height": height,
            "parent": "game-container",
            "physics": {
                "default": physics_type,
                physics_type: {
                    "gravity": {"y": 800 if physics_type == "arcade" else 0},
                    "debug": False
                }
            },
            "scene": {
                "preload": "preload",
                "create": "create",
                "update": "update"
            }
        }
        
        if responsive:
            config["scale"] = {
                "mode": "Phaser.Scale.FIT",
                "autoCenter": "Phaser.Scale.CENTER_BOTH"
            }
        
        return {
            "status": "success",
            "config": config,
            "config_string": self._config_to_string(config)
        }
    
    @kernel_function(
        name="get_input_handler",
        description="Get input handling code for Phaser 3"
    )
    async def get_input_handler(
        self,
        input_types: List[str] = ["keyboard", "mouse"]
    ) -> Dict[str, str]:
        """Generate input handling code for various input types"""
        handlers = []
        
        if "keyboard" in input_types:
            handlers.append(self._get_keyboard_handler())
        if "mouse" in input_types:
            handlers.append(self._get_mouse_handler())
        if "touch" in input_types:
            handlers.append(self._get_touch_handler())
        
        return {
            "status": "success",
            "input_types": input_types,
            "code": "\n\n".join(handlers)
        }
    
    @kernel_function(
        name="get_physics_setup",
        description="Get physics setup code for different game types"
    )
    async def get_physics_setup(
        self,
        game_type: str = "platformer"
    ) -> Dict[str, str]:
        """Generate physics setup code based on game type"""
        physics_setups = {
            "platformer": self._get_platformer_physics(),
            "shooter": self._get_shooter_physics(),
            "puzzle": self._get_puzzle_physics(),
            "arcade": self._get_arcade_physics()
        }
        
        setup = physics_setups.get(game_type.lower(), physics_setups["arcade"])
        
        return {
            "status": "success",
            "game_type": game_type,
            "physics_code": setup
        }
    
    def _get_basic_template(self) -> str:
        """Get basic Phaser 3 game template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phaser 3 Game</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #2c3e50;
        }
        #game-container {
            border: 2px solid #34495e;
        }
    </style>
</head>
<body>
    <div id="game-container"></div>
    <script>
        // Game configuration
        const config = {
            type: Phaser.AUTO,
            width: 800,
            height: 600,
            parent: 'game-container',
            physics: {
                default: 'arcade',
                arcade: {
                    gravity: { y: 0 },
                    debug: false
                }
            },
            scene: {
                preload: preload,
                create: create,
                update: update
            }
        };

        // Game variables
        let player;
        let cursors;

        // Initialize the game
        const game = new Phaser.Game(config);

        function preload() {
            // Create simple colored rectangles as sprites
            this.load.image('player', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==');
        }

        function create() {
            // Create player
            player = this.physics.add.sprite(400, 300, 'player');
            player.setDisplaySize(50, 50);
            player.setTint(0x00ff00);
            player.setCollideWorldBounds(true);

            // Create cursor keys
            cursors = this.input.keyboard.createCursorKeys();

            // Add welcome text
            this.add.text(400, 50, 'Phaser 3 Game', {
                fontSize: '32px',
                fill: '#fff'
            }).setOrigin(0.5);
        }

        function update() {
            // Player movement
            if (cursors.left.isDown) {
                player.setVelocityX(-160);
            } else if (cursors.right.isDown) {
                player.setVelocityX(160);
            } else {
                player.setVelocityX(0);
            }

            if (cursors.up.isDown) {
                player.setVelocityY(-160);
            } else if (cursors.down.isDown) {
                player.setVelocityY(160);
            } else {
                player.setVelocityY(0);
            }
        }
    </script>
</body>
</html>"""
    
    def _get_platformer_template(self) -> str:
        """Get platformer game template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phaser 3 Platformer</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
    <style>
        body {
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background-color: #1a1a2e;
        }
    </style>
</head>
<body>
    <div id="game-container"></div>
    <script>
        const config = {
            type: Phaser.AUTO,
            width: 800,
            height: 600,
            parent: 'game-container',
            physics: {
                default: 'arcade',
                arcade: {
                    gravity: { y: 800 },
                    debug: false
                }
            },
            scene: {
                preload: preload,
                create: create,
                update: update
            }
        };

        let player;
        let platforms;
        let cursors;
        let score = 0;
        let scoreText;

        const game = new Phaser.Game(config);

        function preload() {
            // Using data URLs for simple colored shapes
            this.load.image('ground', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg==');
            this.load.image('player', 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==');
        }

        function create() {
            // Create platforms
            platforms = this.physics.add.staticGroup();
            platforms.create(400, 568, 'ground').setScale(800, 64).refreshBody().setTint(0x654321);
            platforms.create(600, 400, 'ground').setScale(200, 20).refreshBody().setTint(0x654321);
            platforms.create(50, 250, 'ground').setScale(200, 20).refreshBody().setTint(0x654321);
            platforms.create(750, 220, 'ground').setScale(200, 20).refreshBody().setTint(0x654321);

            // Create player
            player = this.physics.add.sprite(100, 450, 'player');
            player.setDisplaySize(32, 48);
            player.setTint(0x00ff00);
            player.setBounce(0.2);
            player.setCollideWorldBounds(true);

            // Player physics
            this.physics.add.collider(player, platforms);

            // Controls
            cursors = this.input.keyboard.createCursorKeys();

            // Score
            scoreText = this.add.text(16, 16, 'Score: 0', { fontSize: '32px', fill: '#fff' });
        }

        function update() {
            // Player movement
            if (cursors.left.isDown) {
                player.setVelocityX(-160);
            } else if (cursors.right.isDown) {
                player.setVelocityX(160);
            } else {
                player.setVelocityX(0);
            }

            // Jump only when on ground
            if (cursors.up.isDown && player.body.touching.down) {
                player.setVelocityY(-500);
            }
        }
    </script>
</body>
</html>"""
    
    def _get_shooter_template(self) -> str:
        """Get shooter game template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phaser 3 Shooter</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
</head>
<body>
    <script>
        // Shooter game template code here
    </script>
</body>
</html>"""
    
    def _get_puzzle_template(self) -> str:
        """Get puzzle game template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phaser 3 Puzzle</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
</head>
<body>
    <script>
        // Puzzle game template code here
    </script>
</body>
</html>"""
    
    def _get_arcade_template(self) -> str:
        """Get arcade game template"""
        return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Phaser 3 Arcade</title>
    <script src="https://cdn.jsdelivr.net/npm/phaser@3.70.0/dist/phaser.min.js"></script>
</head>
<body>
    <script>
        // Arcade game template code here
    </script>
</body>
</html>"""
    
    def _config_to_string(self, config: dict) -> str:
        """Convert config dict to JavaScript string"""
        import json
        return f"const config = {json.dumps(config, indent=4)};"
    
    def _get_keyboard_handler(self) -> str:
        """Get keyboard input handler code"""
        return """// Keyboard input
const cursors = this.input.keyboard.createCursorKeys();
const wasd = this.input.keyboard.addKeys('W,S,A,D');
const spaceBar = this.input.keyboard.addKey(Phaser.Input.Keyboard.KeyCodes.SPACE);

// In update function:
if (cursors.left.isDown || wasd.A.isDown) {
    player.setVelocityX(-160);
} else if (cursors.right.isDown || wasd.D.isDown) {
    player.setVelocityX(160);
} else {
    player.setVelocityX(0);
}"""
    
    def _get_mouse_handler(self) -> str:
        """Get mouse input handler code"""
        return """// Mouse input
this.input.on('pointerdown', (pointer) => {
    // Handle mouse click
    console.log('Mouse clicked at:', pointer.x, pointer.y);
});

this.input.on('pointermove', (pointer) => {
    // Handle mouse movement
    if (pointer.isDown) {
        // Handle drag
    }
});"""
    
    def _get_touch_handler(self) -> str:
        """Get touch input handler code"""
        return """// Touch input
this.input.on('pointerdown', (pointer) => {
    // Handle touch
    const touchX = pointer.x;
    const touchY = pointer.y;
    
    // Move player towards touch point
    this.physics.moveToObject(player, pointer, 240);
});"""
    
    def _get_platformer_physics(self) -> str:
        """Get platformer physics setup"""
        return """// Platformer physics setup
this.physics.world.gravity.y = 800;

// Player physics
player.setBounce(0.2);
player.setCollideWorldBounds(true);
player.body.setGravityY(300);

// Platform collisions
this.physics.add.collider(player, platforms);

// Jump mechanics
if (cursors.up.isDown && player.body.touching.down) {
    player.setVelocityY(-500);
}"""
    
    def _get_shooter_physics(self) -> str:
        """Get shooter physics setup"""
        return """// Shooter physics setup
this.physics.world.gravity.y = 0;

// Bullet group
const bullets = this.physics.add.group({
    defaultKey: 'bullet',
    maxSize: 10
});

// Enemy collisions
this.physics.add.overlap(bullets, enemies, hitEnemy, null, this);"""
    
    def _get_puzzle_physics(self) -> str:
        """Get puzzle physics setup"""
        return """// Puzzle physics setup
this.physics.world.gravity.y = 0;

// Grid-based movement
const gridSize = 32;
player.setVelocity(0);

// Snap to grid
player.x = Math.round(player.x / gridSize) * gridSize;
player.y = Math.round(player.y / gridSize) * gridSize;"""
    
    def _get_arcade_physics(self) -> str:
        """Get arcade physics setup"""
        return """// Arcade physics setup
this.physics.world.gravity.y = 0;

// Arcade-style movement
player.setDamping(true);
player.setDrag(0.99);
player.setMaxVelocity(300);
player.setBounce(1);"""