import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/ar_overlay.dart';
import 'package:hello_ai_os/ui/object_handles.dart';

void main() {
  testWidgets('AROverlay paints outline', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: AROverlay())),
    );
    // CustomPainter testing is tricky, but ensuring it builds without error is step 1.
    expect(find.byType(CustomPaint), findsOneWidget);
  });

  testWidgets('ObjectHandles interaction', (WidgetTester tester) async {
    await tester.pumpWidget(
      const MaterialApp(home: Scaffold(body: ObjectHandles())),
    );

    await tester.tap(find.byIcon(Icons.touch_app));
    await tester.pump();

    expect(find.text('Object Selected'), findsOneWidget);
  });
}
