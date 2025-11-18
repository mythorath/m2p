import React, { useState, useEffect, useContext } from 'react';
import { GameContext } from '../context/GameContext';
import api from '../services/api';
import './DungeonView.css';

const DungeonView = () => {
  const { wallet, player, socketConnected } = useContext(GameContext);
  const [dungeons, setDungeons] = useState([]);
  const [currentRun, setCurrentRun] = useState(null);
  const [character, setCharacter] = useState(null);
  const [inventory, setInventory] = useState([]);
  const [activeView, setActiveView] = useState('hub'); // hub, run, character, inventory
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [combatLog, setCombatLog] = useState([]);

  // Load initial data
  useEffect(() => {
    if (wallet) {
      loadDungeonData();
    }
  }, [wallet]);

  const loadDungeonData = async () => {
    try {
      setLoading(true);
      const [dungeonsRes, characterRes, runRes, inventoryRes] = await Promise.all([
        api.get(`/api/dungeons?wallet=${wallet}`),
        api.get(`/api/character?wallet=${wallet}`),
        api.get(`/api/dungeon/current?wallet=${wallet}`),
        api.get(`/api/inventory?wallet=${wallet}`),
      ]);

      setDungeons(dungeonsRes.data);
      setCharacter(characterRes.data);
      setCurrentRun(runRes.data.run);
      setInventory(inventoryRes.data);

      // If there's an active run, switch to run view
      if (runRes.data.run) {
        setActiveView('run');
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading dungeon data:', err);
      setError('Failed to load dungeon data');
      setLoading(false);
    }
  };

  const startDungeon = async (dungeonId) => {
    try {
      const response = await api.post('/api/dungeon/start', {
        wallet,
        dungeon_id: dungeonId,
      });

      setCurrentRun(response.data.run);
      setCharacter(response.data.character);
      setActiveView('run');
      setCombatLog([]);
      addToCombatLog(`Entered ${response.data.run.dungeon.name}!`, 'info');
    } catch (err) {
      console.error('Error starting dungeon:', err);
      alert(err.response?.data?.error || 'Failed to start dungeon');
    }
  };

  const exploreDungeon = async () => {
    if (!currentRun) return;

    try {
      const response = await api.post('/api/dungeon/explore', {
        wallet,
        run_id: currentRun.id,
      });

      setCurrentRun(response.data.run);
      const encounter = response.data.encounter;

      if (encounter.type === 'monster') {
        addToCombatLog(`💀 Encountered: ${encounter.monster.name} (Lv${encounter.monster.level})`, 'danger');
      } else if (encounter.type === 'treasure') {
        addToCombatLog(`💰 Found a treasure room!`, 'success');
      } else if (encounter.type === 'rest') {
        addToCombatLog(`💚 Rest area - Healed ${encounter.healed} HP`, 'success');
      }

      loadDungeonData(); // Refresh data
    } catch (err) {
      console.error('Error exploring:', err);
      addToCombatLog(`Error: ${err.response?.data?.error || 'Failed to explore'}`, 'danger');
    }
  };

  const attackMonster = async (action = 'attack') => {
    if (!currentRun) return;

    try {
      const response = await api.post('/api/dungeon/combat/attack', {
        wallet,
        run_id: currentRun.id,
        action,
      });

      const result = response.data;

      if (result.player_damage_dealt > 0) {
        addToCombatLog(`⚔️ You dealt ${result.player_damage_dealt} damage!`, 'info');
      }

      if (result.monster_damage_dealt > 0) {
        addToCombatLog(`🩸 You took ${result.monster_damage_dealt} damage!`, 'danger');
      }

      if (result.victory) {
        addToCombatLog(`🎉 Victory! +${result.rewards.exp} EXP`, 'success');
        if (result.rewards.levels_gained > 0) {
          addToCombatLog(`⬆️ Level Up! Now level ${character.level + result.rewards.levels_gained}`, 'success');
        }
        if (result.rewards.loot && result.rewards.loot.length > 0) {
          result.rewards.loot.forEach(item => {
            addToCombatLog(`✨ Found: ${item.name} (${item.rarity})`, 'success');
          });
        }
      }

      if (result.player_defeated) {
        addToCombatLog(`💀 You were defeated! Lost all unclaimed loot.`, 'danger');
        setTimeout(() => {
          setActiveView('hub');
          loadDungeonData();
        }, 2000);
      }

      loadDungeonData(); // Refresh data
    } catch (err) {
      console.error('Error in combat:', err);
      addToCombatLog(`Error: ${err.response?.data?.error || 'Combat failed'}`, 'danger');
    }
  };

  const fleeCombat = async () => {
    if (!currentRun) return;

    try {
      const response = await api.post('/api/dungeon/combat/flee', {
        wallet,
        run_id: currentRun.id,
      });

      if (response.data.fled) {
        addToCombatLog(`🏃 Successfully fled from combat!`, 'info');
      } else if (response.data.flee_failed) {
        addToCombatLog(`❌ Failed to escape!`, 'danger');
        if (response.data.monster_damage_dealt > 0) {
          addToCombatLog(`🩸 You took ${response.data.monster_damage_dealt} damage!`, 'danger');
        }
      }

      loadDungeonData();
    } catch (err) {
      console.error('Error fleeing:', err);
      addToCombatLog(`Error: ${err.response?.data?.error || 'Failed to flee'}`, 'danger');
    }
  };

  const advanceFloor = async () => {
    if (!currentRun) return;

    try {
      const response = await api.post('/api/dungeon/advance-floor', {
        wallet,
        run_id: currentRun.id,
      });

      addToCombatLog(`📈 Advanced to floor ${response.data.current_floor}!`, 'info');
      loadDungeonData();
    } catch (err) {
      console.error('Error advancing floor:', err);
      alert(err.response?.data?.error || 'Failed to advance floor');
    }
  };

  const completeDungeon = async () => {
    if (!currentRun) return;

    try {
      const response = await api.post('/api/dungeon/complete', {
        wallet,
        run_id: currentRun.id,
      });

      addToCombatLog(`🏆 Dungeon completed! Claimed all loot!`, 'success');
      setTimeout(() => {
        setActiveView('hub');
        loadDungeonData();
      }, 2000);
    } catch (err) {
      console.error('Error completing dungeon:', err);
      alert(err.response?.data?.error || 'Failed to complete dungeon');
    }
  };

  const abandonDungeon = async () => {
    if (!currentRun) return;
    if (!window.confirm('Are you sure? You will lose all unclaimed loot!')) return;

    try {
      await api.post('/api/dungeon/abandon', {
        wallet,
        run_id: currentRun.id,
      });

      addToCombatLog(`Abandoned dungeon. Lost unclaimed loot.`, 'danger');
      setTimeout(() => {
        setActiveView('hub');
        loadDungeonData();
      }, 1500);
    } catch (err) {
      console.error('Error abandoning dungeon:', err);
      alert(err.response?.data?.error || 'Failed to abandon dungeon');
    }
  };

  const equipGear = async (inventoryId) => {
    try {
      await api.post(`/api/inventory/equip/${inventoryId}`, { wallet });
      loadDungeonData();
      alert('Gear equipped!');
    } catch (err) {
      console.error('Error equipping gear:', err);
      alert(err.response?.data?.error || 'Failed to equip gear');
    }
  };

  const sellGear = async (inventoryId) => {
    if (!window.confirm('Sell this item?')) return;

    try {
      const response = await api.post(`/api/inventory/sell/${inventoryId}`, { wallet });
      loadDungeonData();
      alert(`Sold for ${response.data.ap_gained} AP!`);
    } catch (err) {
      console.error('Error selling gear:', err);
      alert(err.response?.data?.error || 'Failed to sell gear');
    }
  };

  const addToCombatLog = (message, type = 'info') => {
    setCombatLog(prev => [...prev, { message, type, time: Date.now() }]);
  };

  const getRarityColor = (rarity) => {
    const colors = {
      common: '#9e9e9e',
      uncommon: '#4caf50',
      rare: '#2196f3',
      epic: '#9c27b0',
      legendary: '#ff9800',
    };
    return colors[rarity] || colors.common;
  };

  if (loading) {
    return <div className="dungeon-view loading">Loading dungeon data...</div>;
  }

  if (error) {
    return <div className="dungeon-view error">{error}</div>;
  }

  if (!character) {
    return <div className="dungeon-view">No character data available</div>;
  }

  return (
    <div className="dungeon-view">
      {/* Navigation Bar */}
      <div className="dungeon-nav">
        <button
          className={activeView === 'hub' ? 'active' : ''}
          onClick={() => setActiveView('hub')}
        >
          🏰 Dungeons
        </button>
        {currentRun && (
          <button
            className={activeView === 'run' ? 'active' : ''}
            onClick={() => setActiveView('run')}
          >
            ⚔️ Active Run
          </button>
        )}
        <button
          className={activeView === 'character' ? 'active' : ''}
          onClick={() => setActiveView('character')}
        >
          👤 Character
        </button>
        <button
          className={activeView === 'inventory' ? 'active' : ''}
          onClick={() => setActiveView('inventory')}
        >
          🎒 Inventory ({inventory.length})
        </button>
      </div>

      {/* Dungeon Hub View */}
      {activeView === 'hub' && (
        <div className="dungeon-hub">
          <h2>Available Dungeons</h2>
          <div className="character-summary">
            <span>Level: {character.level}</span>
            <span>HP: {character.health}/{character.max_health}</span>
            <span>ATK: {character.total_attack}</span>
            <span>DEF: {character.total_defense}</span>
            <span>AP: {player?.available_ap || 0}</span>
          </div>

          <div className="dungeon-list">
            {dungeons.map(dungeon => (
              <div key={dungeon.id} className="dungeon-card">
                <h3>{dungeon.name}</h3>
                <div className="dungeon-difficulty">
                  {'⭐'.repeat(dungeon.difficulty)}
                </div>
                <p>{dungeon.description}</p>
                <div className="dungeon-stats">
                  <span>Min Level: {dungeon.min_level_required}</span>
                  <span>Cost: {dungeon.ap_cost_per_run} AP</span>
                  <span>Floors: {dungeon.max_floors}</span>
                </div>
                <div className="dungeon-requirements">
                  {!dungeon.can_enter && (
                    <span className="requirement-failed">
                      ❌ Requires Level {dungeon.min_level_required}
                    </span>
                  )}
                  {!dungeon.can_afford && (
                    <span className="requirement-failed">
                      ❌ Insufficient AP
                    </span>
                  )}
                </div>
                <button
                  onClick={() => startDungeon(dungeon.id)}
                  disabled={!dungeon.can_enter || !dungeon.can_afford}
                  className="start-dungeon-btn"
                >
                  Enter Dungeon
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Active Dungeon Run View */}
      {activeView === 'run' && currentRun && (
        <div className="dungeon-run">
          <div className="run-header">
            <h2>{currentRun.dungeon.name}</h2>
            <div className="run-stats">
              <span>Floor: {currentRun.current_floor}/{currentRun.dungeon.max_floors}</span>
              <span>HP: {character.health}/{character.max_health}</span>
              <span>Monsters: {currentRun.monsters_defeated}</span>
            </div>
          </div>

          {/* Combat Log */}
          <div className="combat-log">
            {combatLog.slice(-10).map((log, idx) => (
              <div key={log.time + idx} className={`log-entry log-${log.type}`}>
                {log.message}
              </div>
            ))}
          </div>

          {/* Combat Interface */}
          {currentRun.combat_state ? (
            <div className="combat-interface">
              <h3>⚔️ Combat!</h3>
              <div className="combat-info">
                <div className="enemy-info">
                  <p>Enemy HP: {currentRun.combat_state.monster_health}</p>
                </div>
                <div className="player-info">
                  <p>Your HP: {character.health}/{character.max_health}</p>
                </div>
              </div>
              <div className="combat-actions">
                <button onClick={() => attackMonster('attack')} className="btn-attack">
                  ⚔️ Attack
                </button>
                <button onClick={() => attackMonster('defend')} className="btn-defend">
                  🛡️ Defend
                </button>
                <button onClick={fleeCombat} className="btn-flee">
                  🏃 Flee
                </button>
              </div>
            </div>
          ) : (
            <div className="exploration-interface">
              <h3>Exploration</h3>
              <div className="exploration-actions">
                <button onClick={exploreDungeon} className="btn-explore">
                  🔍 Explore Room
                </button>
                {currentRun.current_floor < currentRun.dungeon.max_floors && (
                  <button onClick={advanceFloor} className="btn-advance">
                    📈 Next Floor
                  </button>
                )}
                <button onClick={completeDungeon} className="btn-complete">
                  🏆 Complete & Claim Loot
                </button>
                <button onClick={abandonDungeon} className="btn-abandon">
                  🚪 Abandon
                </button>
              </div>
              {currentRun.unclaimed_loot && currentRun.unclaimed_loot.length > 0 && (
                <div className="unclaimed-loot">
                  <p>💰 Unclaimed Loot: {currentRun.unclaimed_loot.length} items</p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Character View */}
      {activeView === 'character' && (
        <div className="character-view">
          <h2>Character Stats</h2>
          <div className="character-stats-detailed">
            <div className="stat-row">
              <span className="stat-label">Level:</span>
              <span className="stat-value">{character.level}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Experience:</span>
              <span className="stat-value">{character.current_exp} / {character.exp_to_next_level}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Health:</span>
              <span className="stat-value">{character.health} / {character.max_health}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Attack:</span>
              <span className="stat-value">{character.attack} (Total: {character.total_attack})</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Defense:</span>
              <span className="stat-value">{character.defense} (Total: {character.total_defense})</span>
            </div>
          </div>

          <h3>Equipment</h3>
          <div className="equipment-slots">
            <div className="equipment-slot">
              <span className="slot-label">Weapon:</span>
              {character.equipped_weapon ? (
                <div className="equipped-item" style={{ borderColor: getRarityColor(character.equipped_weapon.rarity) }}>
                  {character.equipped_weapon.name}
                  <small>+{character.equipped_weapon.stat_bonuses.attack} ATK</small>
                </div>
              ) : (
                <span className="empty-slot">None</span>
              )}
            </div>
            <div className="equipment-slot">
              <span className="slot-label">Armor:</span>
              {character.equipped_armor ? (
                <div className="equipped-item" style={{ borderColor: getRarityColor(character.equipped_armor.rarity) }}>
                  {character.equipped_armor.name}
                  <small>+{character.equipped_armor.stat_bonuses.defense} DEF</small>
                </div>
              ) : (
                <span className="empty-slot">None</span>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Inventory View */}
      {activeView === 'inventory' && (
        <div className="inventory-view">
          <h2>Inventory</h2>
          {inventory.length === 0 ? (
            <p className="empty-inventory">No items in inventory</p>
          ) : (
            <div className="inventory-grid">
              {inventory.map(item => (
                <div
                  key={item.id}
                  className="inventory-item"
                  style={{ borderColor: getRarityColor(item.gear.rarity) }}
                >
                  <h4>{item.gear.name}</h4>
                  <span className={`rarity rarity-${item.gear.rarity}`}>
                    {item.gear.rarity}
                  </span>
                  <p className="item-type">{item.gear.type}</p>
                  <div className="item-stats">
                    {Object.entries(item.gear.stat_bonuses).map(([stat, value]) => (
                      <span key={stat}>+{value} {stat.toUpperCase()}</span>
                    ))}
                  </div>
                  <div className="item-actions">
                    {!item.is_equipped ? (
                      <button onClick={() => equipGear(item.id)} className="btn-equip">
                        Equip
                      </button>
                    ) : (
                      <span className="equipped-badge">✓ Equipped</span>
                    )}
                    <button onClick={() => sellGear(item.id)} className="btn-sell" disabled={item.is_equipped}>
                      Sell ({item.gear.sell_value} AP)
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DungeonView;
