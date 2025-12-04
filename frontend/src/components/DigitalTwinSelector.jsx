import React from 'react';
import { ChevronDown } from 'lucide-react';
import './DigitalTwinSelector.css';

const DIGITAL_TWINS = [
    { id: 12288, name: 'Heat Exchanger HX17-A1', type: 'HeatExchanger' },
    { id: 24808, name: 'Equipment Unit EU-24808', type: 'Equipment' },
    { id: 40976504, name: 'Heat Exchanger HX00-A3', type: 'HeatExchanger' },
    { id: 28904, name: 'Equipment Unit EU-28904', type: 'Equipment' },
    { id: 40964304, name: 'Equipment Unit EU-40964304', type: 'Equipment' }
];

const DigitalTwinSelector = ({ selectedTwin, onSelectTwin }) => {
    return (
        <div className="twin-selector">
            <label htmlFor="twin-select">Select Digital Twin:</label>
            <div className="select-wrapper">
                <select
                    id="twin-select"
                    value={selectedTwin?.id || ''}
                    onChange={(e) => {
                        const twin = DIGITAL_TWINS.find(t => t.id === parseInt(e.target.value));
                        onSelectTwin(twin);
                    }}
                >
                    <option value="">Choose an entity...</option>
                    {DIGITAL_TWINS.map(twin => (
                        <option key={twin.id} value={twin.id}>
                            {twin.name} (ID: {twin.id})
                        </option>
                    ))}
                </select>
                <ChevronDown className="select-icon" size={20} />
            </div>
            {selectedTwin && (
                <div className="selected-info">
                    <span className="badge">{selectedTwin.type}</span>
                    <span className="entity-id">ID: {selectedTwin.id}</span>
                </div>
            )}
        </div>
    );
};

export default DigitalTwinSelector;
