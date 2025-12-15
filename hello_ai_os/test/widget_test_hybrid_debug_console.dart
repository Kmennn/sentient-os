import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/hybrid_debug_console.dart';

void main() {
  testWidgets('Debug Console Visualization', (WidgetTester tester) async {
    final events = [
      {"timestamp": "2025-01-01T12:00:00", "type": "INFO", "message": "Init"},
      {
        "timestamp": "2025-01-01T12:00:01",
        "type": "FALLBACK",
        "message": "Test Fallback",
      },
    ];

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: HybridDebugConsole(
            timelineEvents: events,
            currentAlpha: 0.8,
            isLocked: true,
          ),
        ),
      ),
    );

    expect(find.text('[LOCKED]'), findsOneWidget);
    expect(find.text('0.80'), findsOneWidget);
    expect(find.textContaining('<FALLBACK> Test Fallback'), findsOneWidget);
  });
}
