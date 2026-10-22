=====================================
Fleet operations: the Upgrade Console
=====================================

A chain does not have one server to look after. It has a head office that may run on several nodes
and dozens of stores, each on a machine in a branch office. The **Upgrade Console**
(`mtl_upgrade_console`) is an Odoo application that shows the whole fleet on one screen and lets
an administrator act on it: upgrade, scale, switch a database, change a licensing mode. Nothing
else is installed on the servers except a small agent.

.. graphviz::
   :caption: One console, an agent next to every target

   digraph fleet {
      rankdir=LR;
      node [shape=box, style="rounded,filled", fillcolor="#F8F8F8", color="#D5D5D5"];
      edge [color="#888888"];
      con [label="Upgrade Console\n(Odoo app)", fillcolor="#f3eef1", color="#714B67"];
      { rank=same;
        ho [label="HO agent\nHO stack"];
        s1 [label="Store agent\nstore stack"];
        s2 [label="Store agent\nstore stack"]; }
      con -> ho [label="jobs", fontcolor="#888888"];
      con -> s1;
      con -> s2;
      ho -> con [label="heartbeat,\nKPIs", fontcolor="#888888", constraint=false];
   }

What the console shows
======================

Each target (the head office, or a store) has an **agent**, a small container next to it that
reports in on a fixed beat: running version, last upgrade, host CPUs, free memory and disk use,
and for every container its health, memory against its limit and, on a swarm, service availability
and failed tasks in the last hour. A target that stops beating is flagged **stale** on the dashboard within thirty
seconds, and an alert fires from a scheduled check and from the other agents' beats, so a silent
store is noticed even if the console itself is quiet.

What the console does
=====================

Upgrade now
   One click starts the same pipeline that Git triggers (see :doc:`cicd`): build the release,
   migrate the databases, roll the nodes. The console shows each phase as it runs and the result
   at the end. A target has its own **auto-upgrade switch**, so a store can follow Git
   automatically while another is held back for a busy week.

Upgrade chosen stores
   Pick any set of stores and upgrade just those, one after another, with a dry run that lists
   what *would* change before anything does. A store that fails stops the run instead of silently
   continuing.

Scale
   Add or remove user-interface nodes on the head office for the festive season and back, with
   the new count and the result recorded.

Thresholds
   Warning and critical levels for host memory and disk, container memory and health, service
   availability and failed tasks, set for all targets or overridden per environment, so alerts are
   tuned to each machine rather than a global guess.

Primary and secondary databases
   Map each store to a **primary and a secondary database**, for example the production copy and a
   freshly restored one. The console **switches the stack from one to the other as a rolling
   change**, a node at a time, and verifies connectivity before it moves on. A mapping with the
   wrong credentials is detected and never pushed.

Licensing mode
   The head office can run **with or without the vendor's publisher-warranty channel**. The console
   switches the HO between the two deployment variants, and for the no-warranty variant it replaces
   the licence call with a local stub and keeps the real enterprise code safely backed up in the
   database so the switch can be reversed. Stores do not need it.

Safety rules built in
=====================

* Agents authenticate with a token that is stored on the target, never in the repository.
* Secrets set in the console are visible only to administrators.
* A target with auto-upgrade off stays untouched by scheduled runs, whatever Git does.
* An upgrade that cannot start a node healthy **rolls back automatically**; the console shows the
  rollback as a result, not a silent failure.
* Every action is recorded: who, which target, which phase, and its output.
