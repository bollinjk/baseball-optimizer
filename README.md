# Baseball Lineup Optimizer - Phillies Edition

A web-based tool for optimizing baseball lineups to maximize run production.

## Features

- **Complete Baseball Simulation**: Simulates realistic baseball games with 6 innings
- **Dual Optimization Methods**:
  - Quick Analysis: Uses random sampling for fast results
  - Deep Analysis: Tests all possible lineup permutations for optimal results
- **Player Management**: Edit existing players or add new ones
- **Detailed Statistics**: Inning-by-inning analysis with comprehensive metrics
- **Save/Load Functionality**: Save your optimized lineups for future reference
- **Cross-Platform Compatible**: Works on any device with a modern web browser

## How to Use

1. Open `index.html` in any web browser
2. Review and edit the default roster if needed
3. Click "Start Optimization" to begin the analysis
4. View results showing best lineup configurations
5. Save your optimized lineups using the "Save Lineups" button

## Quick Start

Simply double-click the `index.html` file to open in your default browser. No installation required!

## Technical Details

- Pure HTML/CSS/JavaScript implementation
- No external dependencies
- Uses Web Workers for parallel processing
- LocalStorage for saving state

## Default Player Stats

The tool comes preloaded with the following player data:
- Jeremiah: 90% hit chance (60% singles, 30% doubles, 10% triples)
- Calvin: 90% hit chance (60% singles, 30% doubles, 10% triples)
- Ty: 40% hit chance (90% singles, 10% doubles)
- Dean: 60% hit chance (90% singles, 10% doubles)
- Harrison: 20% hit chance (100% singles)
- Kai: 35% hit chance (60% singles, 30% doubles, 10% triples)
- Theo: 25% hit chance (95% singles, 5% doubles)
- Bob: 80% hit chance (80% singles, 20% doubles)
- Joe: 47% hit chance (100% singles)
- Matt: 60% hit chance (100% singles)
- Arnold: 50% hit chance (100% singles)

## Optimization Logic

The application simulates baseball games with the following rules:
- 6 innings per game
- 3 outs per inning
- Maximum 5 runs per inning
- Players advance bases based on hit type
- Runner advancement is proportional to hit type

Created with ❤️ using Phillies colors and styling.
