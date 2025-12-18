import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:hello_ai_os/ui/routine_panel.dart';

void main() {
  testWidgets('Displays routines and toggles', (WidgetTester tester) async {
    final r = RoutineItem(
      id: '1',
      name: 'Morning Login',
      timeWindow: '09:00',
      confidence: 0.9,
      protected: false,
    );

    bool toggled = false;

    await tester.pumpWidget(
      MaterialApp(
        home: Scaffold(
          body: RoutinePanel(
            routines: [r],
            onProtectionToggled: (id, val) => toggled = true,
          ),
        ),
      ),
    );

    expect(find.text('Detected Routines'), findsOneWidget);
    expect(find.text('Morning Login'), findsOneWidget);
    expect(find.text('09:00 • Conf: 90%'), findsOneWidget);

    await tester.tap(find.byType(SwitchListTile));
    expect(toggled, isTrue);
  });
}
