import 'package:flutter/material.dart';

class DepthOverlay extends StatelessWidget {
  const DepthOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return IgnorePointer(
      child: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.red.withValues(alpha: 0.3), // Far
              Colors.blue.withValues(alpha: 0.3), // Near
            ],
          ),
        ),
        child: const Center(
          child: Text(
            "Depth Estimation: ON",
            style: TextStyle(
              color: Colors.white,
              backgroundColor: Colors.black54,
            ),
          ),
        ),
      ),
    );
  }
}
