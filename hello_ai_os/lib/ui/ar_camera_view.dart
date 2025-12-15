import 'package:flutter/material.dart';

class ARCameraView extends StatelessWidget {
  const ARCameraView({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          // 1. Camera Feed Placeholder (In real app, CameraPreview)
          Container(
            width: double.infinity,
            height: double.infinity,
            color: Colors.grey[900],
            child: const Center(
              child: Icon(Icons.videocam_off, color: Colors.white54, size: 64),
            ),
          ),

          // 2. Spatial Overlay
          const Positioned.fill(child: SpatialOverlay()),

          // 3. HUD Controls
          Positioned(
            bottom: 30,
            left: 0,
            right: 0,
            child: Center(
              child: FloatingActionButton.extended(
                icon: const Icon(Icons.radar),
                label: const Text("Scan Space"),
                onPressed: () {},
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class SpatialOverlay extends StatelessWidget {
  const SpatialOverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(
      painter: SpatialGridPainter(),
      child: GestureDetector(
        behavior: HitTestBehavior.opaque,
        onTapUp: (details) {
          // Raycast logic would go here
          print("Tap at ${details.localPosition}");
        },
      ),
    );
  }
}

class SpatialGridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.green.withOpacity(0.3)
      ..strokeWidth = 1.0
      ..style = PaintingStyle.stroke;

    // Draw grid lines to simulate "floor" detection
    double step = 50.0;
    for (double x = 0; x < size.width; x += step) {
      canvas.drawLine(
        Offset(x, size.height / 2),
        Offset(x + size.width / 4, size.height),
        paint,
      );
    }

    // Draw horizon
    canvas.drawLine(
      Offset(0, size.height / 2),
      Offset(size.width, size.height / 2),
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
