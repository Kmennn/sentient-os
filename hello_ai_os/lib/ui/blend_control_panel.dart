import 'package:flutter/material.dart';

class BlendControlPanel extends StatefulWidget {
  final double currentAlpha;
  final Function(double) onAlphaChanged;
  final bool isUnstable;

  const BlendControlPanel({
    super.key,
    required this.currentAlpha,
    required this.onAlphaChanged,
    this.isUnstable = false,
  });

  @override
  State<BlendControlPanel> createState() => _BlendControlPanelState();
}

class _BlendControlPanelState extends State<BlendControlPanel> {
  @override
  Widget build(BuildContext context) {
    return Card(
      color: Colors.deepPurple[900],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  "Hybrid Planning Control",
                  style: TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                if (widget.isUnstable)
                  const Chip(
                    label: Text("UNSTABLE - FALLBACK"),
                    backgroundColor: Colors.red,
                    labelStyle: TextStyle(color: Colors.white, fontSize: 10),
                  ),
              ],
            ),
            const SizedBox(height: 16),

            Text(
              "Policy Influence: ${(1.0 - widget.currentAlpha) * 100}%",
              style: const TextStyle(color: Colors.cyanAccent),
            ),
            Text(
              "Planner Authority: ${widget.currentAlpha * 100}%",
              style: const TextStyle(color: Colors.orangeAccent),
            ),

            Slider(
              value: widget.currentAlpha,
              min: 0.0,
              max: 1.0,
              divisions: 10,
              activeColor: Colors.orangeAccent,
              inactiveColor: Colors.cyanAccent,
              label: "Alpha: ${widget.currentAlpha}",
              onChanged: widget.isUnstable
                  ? null
                  : widget
                        .onAlphaChanged, // Disabled if unstable? Or allow user to reset?
              // Logic: If unstable, system forces 1.0. User can try to drag back, but system might override.
              // For UI, let's enable it so user can try to re-engage policy.
            ),

            const Center(
              child: Text(
                "Drag Left (Cyan) for intuition, Right (Orange) for safety.",
                style: TextStyle(color: Colors.grey, fontSize: 10),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
