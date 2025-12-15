import 'package:flutter/material.dart';

class AROverlay extends StatelessWidget {
  const AROverlay({super.key});

  @override
  Widget build(BuildContext context) {
    return CustomPaint(painter: ARPainter(), child: Container());
  }
}

class ARPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.greenAccent
      ..style = PaintingStyle.stroke
      ..strokeWidth = 2.0;

    // Simulate drawing a bounding box around a detected object
    // In real app, this would come from SpatialMesh state
    final rect = Rect.fromCenter(
      center: Offset(size.width / 2, size.height / 2),
      width: 100,
      height: 100,
    );

    canvas.drawRect(rect, paint);

    // Draw label
    final textSpan = TextSpan(
      text: 'Object (Depth: 0.5m)',
      style: TextStyle(color: Colors.greenAccent, fontSize: 12),
    );
    final textPainter = TextPainter(
      text: textSpan,
      textDirection: TextDirection.ltr,
    );
    textPainter.layout();
    textPainter.paint(canvas, Offset(rect.left, rect.top - 15));
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
