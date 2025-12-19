import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:hello_ai_os/services/state_stream_service.dart';
import 'package:hello_ai_os/ui/widgets/glass_container.dart';
import 'package:hello_ai_os/ui/timeline_page.dart';

class SystemStatusPanel extends StatelessWidget {
  const SystemStatusPanel({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      appBar: AppBar(
        title: const Text("System Transparency"),
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.psychology, color: Colors.cyanAccent),
            label: const Text(
              "Brain Log",
              style: TextStyle(color: Colors.cyanAccent),
            ),
            onPressed: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const TimelinePage()),
              );
            },
          ),
        ],
      ),
      body: StreamBuilder<Map<String, dynamic>>(
        stream: stateStreamService.stateStream,
        initialData: stateStreamService.lastState,
        builder: (context, snapshot) {
          final data = snapshot.data ?? {};
          if (data.isEmpty) {
            return const Center(child: CircularProgressIndicator());
          }

          final activeDev = data['active_device'] ?? "Unknown";
          final devTrust = data['device_trust_score'] ?? 0.0;
          final confLevel = data['confidence_level'] ?? "MED";

          final focusState = data['focus_state'] ?? "free";
          final presence = data['presence_state'] ?? "unknown";

          final intStyle = data['interrupt_style'] ?? "unknown";
          final gate = data['last_attention_gate_decision'] ?? "SILENT";

          final deviceList = data['device_list'] as List? ?? [];

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _SectionHeader(title: "ACTIVE CONTEXT", icon: Icons.radar),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: _StatusCard(
                        label: "Active Device",
                        value: activeDev.toUpperCase(),
                        subValue:
                            "Trust: ${(devTrust * 100).toInt()}% ($confLevel)",
                        icon: Icons.computer,
                        color: _getTrustColor(devTrust),
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _StatusCard(
                        label: "Attention Gate",
                        value: gate.toString().toUpperCase(),
                        subValue: intStyle.replaceAll("_", " ").toUpperCase(),
                        icon: Icons.security,
                        color: gate == "ALLOW"
                            ? Colors.greenAccent
                            : Colors.orangeAccent,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),
                _SectionHeader(title: "USER STATE", icon: Icons.person_outline),
                const SizedBox(height: 10),
                Row(
                  children: [
                    Expanded(
                      child: _StatusCard(
                        label: "Focus",
                        value: focusState.toString().toUpperCase(),
                        subValue: focusState == "focus_session"
                            ? "Mode: Deep Work"
                            : "Mode: Available",
                        icon: Icons.center_focus_strong,
                        color: focusState == "focus_session"
                            ? Colors.purpleAccent
                            : Colors.blueGrey,
                      ),
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: _StatusCard(
                        label: "Presence",
                        value: presence.toString().toUpperCase(),
                        subValue: presence == "with_others"
                            ? "Social Mode"
                            : "Private",
                        icon: Icons.groups,
                        color: presence == "with_others"
                            ? Colors.blueAccent
                            : Colors.grey,
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 20),
                _SectionHeader(
                  title: "DEVICE & TRUST REGISTRY",
                  icon: Icons.devices,
                ),
                const SizedBox(height: 10),
                ...deviceList.map((d) {
                  final trust = d['trust'] ?? 0.0;
                  final isActive = d['active'] ?? false;
                  return _DeviceTile(
                    name: d['id'] ?? "Unknown",
                    type: d['type'] ?? "Generic",
                    trust: trust,
                    isActive: isActive,
                  );
                }),

                const SizedBox(height: 30),
                _SectionHeader(title: "MANUAL OVERRIDES", icon: Icons.tune),
                const SizedBox(height: 10),
                GlassContainer(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _ControlRow(
                        label: "Focus Mode",
                        child: Row(
                          children: [
                            if (focusState == "focus_session")
                              _ControlButton(
                                label: "STOP FOCUS",
                                color: Colors.redAccent,
                                onTap: () => _apiCall("/focus/stop"),
                              )
                            else
                              _ControlButton(
                                label: "START 25m",
                                color: Colors.purpleAccent,
                                onTap: () => _apiCall(
                                  "/focus/start?duration_minutes=25",
                                  method: "POST",
                                ),
                              ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      _ControlRow(
                        label: "Presence",
                        child: Row(
                          children: [
                            _ControlButton(
                              label: "PRIVATE",
                              color: presence == "alone"
                                  ? Colors.green
                                  : Colors.grey,
                              onTap: () =>
                                  _apiCall("/presence/private", method: "POST"),
                              isActive: presence == "alone",
                            ),
                            const SizedBox(width: 8),
                            _ControlButton(
                              label: "PUBLIC",
                              color: presence == "with_others"
                                  ? Colors.green
                                  : Colors.grey,
                              onTap: () =>
                                  _apiCall("/presence/public", method: "POST"),
                              isActive: presence == "with_others",
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 16),
                      _ControlRow(
                        label: "Interrupts",
                        child: DropdownButton<String>(
                          value: intStyle,
                          dropdownColor: Colors.grey[900],
                          style: const TextStyle(
                            color: Colors.white,
                            fontSize: 12,
                          ),
                          onChanged: (val) {
                            if (val != null) {
                              _apiCall(
                                "/settings/interrupt-style?style=$val",
                                method: "POST",
                              );
                            }
                          },
                          items:
                              [
                                    "never_interrupt",
                                    "ask_for_important",
                                    "always_ask",
                                  ]
                                  .map(
                                    (s) => DropdownMenuItem(
                                      value: s,
                                      child: Text(
                                        s.replaceAll("_", " ").toUpperCase(),
                                      ),
                                    ),
                                  )
                                  .toList(),
                        ),
                      ),
                                    ),
                                  )
                                  .toList(),
                        ),
                      ),
                      const SizedBox(height: 16),
                      _ControlRow(
                        label: "Safe Sandbox",
                        child: _ControlButton(
                            label: "TEST PING",
                            color: Colors.cyanAccent,
                            onTap: () => _apiCall("/actions/demo_safe_ping/execute", method: "POST"),
                        ),
                      ),
                      const SizedBox(height: 8),
                       _ControlRow(
                        label: "Budget Status",
                        child: Text(
                          _budgetStatus,
                          style: TextStyle(
                            color: _budgetStatus == "OK" ? Colors.greenAccent : Colors.orangeAccent,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      const SizedBox(height: 8),
                       _ControlRow(
                        label: "Recovery Mode",
                        child: Tooltip(
                          message: "System is cooling down to avoid errors",
                          child: Text(
                            _recoveryLevel,
                            style: TextStyle(
                              color: _recoveryLevel == "NONE" ? Colors.greenAccent : Colors.redAccent,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          );
        },
      ),
    );
  }

  Future<void> _apiCall(String endpoint, {String method = "POST"}) async {
    // Basic HTTP call - requires http package import
    try {
      // Assuming localhost:8000
      final uri = Uri.parse("http://127.0.0.1:8000$endpoint");
      // Use http.post even if empty body
      // We need to import http.
      // Assuming it's available or I'll use a helper.
      // I'll define a helper using pure dart:io or http if imported.
      // Since I can't easily see imports for this file, I'll add `import 'package:http/http.dart' as http;` to the top.
      await http.post(uri);
    } catch (e) {
      print("API Error: $e");
    }
  }

  Future<void> _checkRecoveryStatus() async {
    try {
      final response = await http.get(Uri.parse('http://127.0.0.1:8000/autonomy/recovery'));
      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          _recoveryLevel = data['level'];
        });
      }
    } catch (e) {
      print("Error fetching recovery: $e");
    }
  }
  
  String _recoveryLevel = "NONE";


  Color _getTrustColor(double score) {
    if (score >= 0.7) return Colors.greenAccent;
    if (score >= 0.4) return Colors.amberAccent;
    return Colors.redAccent;
  }
}

class _ControlRow extends StatelessWidget {
  final String label;
  final Widget child;
  const _ControlRow({required this.label, required this.child});
  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 14),
        ),
        child,
      ],
    );
  }
}

class _ControlButton extends StatelessWidget {
  final String label;
  final Color color;
  final VoidCallback onTap;
  final bool isActive;

  const _ControlButton({
    required this.label,
    required this.color,
    required this.onTap,
    this.isActive = false,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? color.withOpacity(0.2) : Colors.transparent,
          border: Border.all(color: isActive ? color : color.withOpacity(0.5)),
          borderRadius: BorderRadius.circular(4),
        ),
        child: Text(
          label,
          style: TextStyle(
            color: isActive ? color : color.withOpacity(0.8),
            fontWeight: FontWeight.bold,
            fontSize: 10,
          ),
        ),
      ),
    );
  }
}

class _SuggestionCard extends StatelessWidget {
  final String id;
  final String message;
  final String type;
  final Function(String) onResolve;

  const _SuggestionCard({
    required this.id,
    required this.message,
    required this.type,
    required this.onResolve,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 20),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.cyanAccent.withOpacity(0.1),
        border: Border.all(color: Colors.cyanAccent),
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(color: Colors.cyanAccent.withOpacity(0.1), blurRadius: 10),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.lightbulb, color: Colors.cyanAccent, size: 16),
              const SizedBox(width: 8),
              Text(
                "SUGGESTION",
                style: TextStyle(
                  color: Colors.cyanAccent,
                  fontWeight: FontWeight.bold,
                  fontSize: 10,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            message,
            style: const TextStyle(color: Colors.white, fontSize: 14),
          ),
          const SizedBox(height: 12),
          Row(
            mainAxisAlignment: MainAxisAlignment.end,
            children: [
              TextButton(
                onPressed: () => onResolve("DISMISS"),
                child: const Text(
                  "Dismiss",
                  style: TextStyle(color: Colors.white54),
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton(
                onPressed: () => onResolve("ACCEPT"),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.cyanAccent,
                  foregroundColor: Colors.black,
                ),
                child: const Text("Accept"),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final IconData icon;
  const _SectionHeader({required this.title, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 16, color: Colors.white54),
        const SizedBox(width: 8),
        Text(
          title,
          style: const TextStyle(
            color: Colors.white54,
            fontWeight: FontWeight.bold,
            letterSpacing: 1.5,
            fontSize: 12,
          ),
        ),
      ],
    );
  }
}

class _StatusCard extends StatelessWidget {
  final String label;
  final String value;
  final String subValue;
  final IconData icon;
  final Color color;

  const _StatusCard({
    required this.label,
    required this.value,
    required this.subValue,
    required this.icon,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return GlassContainer(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 28),
          const SizedBox(height: 12),
          Text(
            label,
            style: const TextStyle(color: Colors.white54, fontSize: 11),
          ),
          const SizedBox(height: 4),
          Text(
            value,
            style: const TextStyle(
              color: Colors.white,
              fontWeight: FontWeight.bold,
              fontSize: 14,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            subValue,
            style: TextStyle(color: color.withOpacity(0.8), fontSize: 10),
          ),
        ],
      ),
    );
  }
}

class _DeviceTile extends StatelessWidget {
  final String name;
  final String type;
  final double trust;
  final bool isActive;

  const _DeviceTile({
    required this.name,
    required this.type,
    required this.trust,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context) {
    // 0..1 to Color
    final color = trust >= 0.7
        ? Colors.greenAccent
        : (trust >= 0.4 ? Colors.amber : Colors.redAccent);

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.05),
        borderRadius: BorderRadius.circular(8),
        border: isActive
            ? Border.all(color: Colors.cyanAccent.withOpacity(0.5))
            : null,
      ),
      child: Row(
        children: [
          Icon(
            type == "mobile" ? Icons.smartphone : Icons.computer,
            color: Colors.white70,
            size: 20,
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  isActive ? "$name (Active)" : name,
                  style: TextStyle(
                    color: isActive ? Colors.cyanAccent : Colors.white,
                    fontWeight: FontWeight.w600,
                  ),
                ),
                Text(
                  type.toUpperCase(),
                  style: const TextStyle(color: Colors.white38, fontSize: 10),
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                "${(trust * 100).toInt()}%",
                style: TextStyle(color: color, fontWeight: FontWeight.bold),
              ),
              const Text(
                "Trust",
                style: TextStyle(fontSize: 8, color: Colors.white38),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
