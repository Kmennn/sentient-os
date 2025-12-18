import 'package:flutter/material.dart';

enum DelayTolerance { low, medium, high }

class SchedulingPreferencesPanel extends StatefulWidget {
  final DelayTolerance initialTolerance;
  final bool initialPreemption;
  final Function(DelayTolerance)? onToleranceChanged;
  final Function(bool)? onPreemptionChanged;

  const SchedulingPreferencesPanel({
    super.key,
    this.initialTolerance = DelayTolerance.medium,
    this.initialPreemption = false,
    this.onToleranceChanged,
    this.onPreemptionChanged,
  });

  @override
  State<SchedulingPreferencesPanel> createState() =>
      _SchedulingPreferencesPanelState();
}

class _SchedulingPreferencesPanelState
    extends State<SchedulingPreferencesPanel> {
  late DelayTolerance _tolerance;
  late bool _allowPreemption;

  @override
  void initState() {
    super.initState();
    _tolerance = widget.initialTolerance;
    _allowPreemption = widget.initialPreemption;
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.purple[50],
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Row(
              children: const [
                Icon(Icons.tune, color: Colors.purple),
                SizedBox(width: 8),
                Text(
                  'Scheduling Preferences',
                  style: TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),
          ),
          const Divider(height: 1),

          // Delay Tolerance Slider
          ListTile(
            title: const Text("Delay Tolerance"),
            subtitle: Text(_tolerance.name.toUpperCase()),
          ),
          Slider(
            value: _tolerance.index.toDouble(),
            min: 0,
            max: 2,
            divisions: 2,
            label: _tolerance.name.toUpperCase(),
            activeColor: Colors.purple,
            onChanged: (val) {
              setState(() {
                _tolerance = DelayTolerance.values[val.toInt()];
              });
              widget.onToleranceChanged?.call(_tolerance);
            },
          ),

          // Preemption Toggle
          SwitchListTile(
            title: const Text("Allow Preemption"),
            subtitle: const Text(
              "Allow others to interrupt my low-priority tasks",
            ),
            value: _allowPreemption,
            activeThumbColor: Colors.purple,
            onChanged: (val) {
              setState(() {
                _allowPreemption = val;
              });
              widget.onPreemptionChanged?.call(val);
            },
          ),
        ],
      ),
    );
  }
}
