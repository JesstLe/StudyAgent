"""Seed the knowledge graph with core CS concepts and their prerequisite relations."""

from __future__ import annotations

CONCEPTS: list[dict] = [
    # --- Data Structures ---
    {"name": "Array", "domain": "data_structures", "difficulty": 0.2, "description": "Contiguous memory block with O(1) index access"},
    {"name": "Linked List", "domain": "data_structures", "difficulty": 0.25, "description": "Node-based sequential structure with O(1) insertion/deletion"},
    {"name": "Stack", "domain": "data_structures", "difficulty": 0.2, "description": "LIFO structure: push/pop from one end"},
    {"name": "Queue", "domain": "data_structures", "difficulty": 0.2, "description": "FIFO structure: enqueue at back, dequeue from front"},
    {"name": "Hash Table", "domain": "data_structures", "difficulty": 0.35, "description": "Key-value store using hash function for O(1) average lookup"},
    {"name": "Binary Tree", "domain": "data_structures", "difficulty": 0.3, "description": "Hierarchical structure where each node has at most two children"},
    {"name": "Binary Search Tree", "domain": "data_structures", "difficulty": 0.35, "description": "Ordered binary tree: left < root < right, enabling O(log n) search"},
    {"name": "AVL Tree", "domain": "data_structures", "difficulty": 0.5, "description": "Self-balancing BST with height difference ≤ 1"},
    {"name": "Red-Black Tree", "domain": "data_structures", "difficulty": 0.55, "description": "Self-balancing BST with color-based balancing rules"},
    {"name": "B-tree", "domain": "data_structures", "difficulty": 0.55, "description": "Multi-way balanced tree optimized for disk I/O"},
    {"name": "Heap", "domain": "data_structures", "difficulty": 0.35, "description": "Complete binary tree satisfying heap property (min or max)"},
    {"name": "Graph", "domain": "data_structures", "difficulty": 0.4, "description": "Set of vertices connected by edges; models relationships"},
    {"name": "Trie", "domain": "data_structures", "difficulty": 0.4, "description": "Prefix tree for efficient string operations"},
    {"name": "Union-Find", "domain": "data_structures", "difficulty": 0.4, "description": "Disjoint set structure with union and find operations"},
    # --- Algorithms ---
    {"name": "Big-O Notation", "domain": "algorithms", "difficulty": 0.2, "description": "Asymptotic upper bound for algorithm complexity"},
    {"name": "Recursion", "domain": "algorithms", "difficulty": 0.3, "description": "Function calling itself with a smaller subproblem"},
    {"name": "Sorting", "domain": "algorithms", "difficulty": 0.3, "description": "Arranging elements in order (comparison-based and non-comparison)"},
    {"name": "Binary Search", "domain": "algorithms", "difficulty": 0.25, "description": "Divide-and-conquer search on sorted data, O(log n)"},
    {"name": "BFS", "domain": "algorithms", "difficulty": 0.35, "description": "Breadth-First Search: level-order graph traversal using a queue"},
    {"name": "DFS", "domain": "algorithms", "difficulty": 0.35, "description": "Depth-First Search: go deep first using stack/recursion"},
    {"name": "Dynamic Programming", "domain": "algorithms", "difficulty": 0.6, "description": "Optimal substructure + overlapping subproblems → memoization or tabulation"},
    {"name": "Greedy Algorithm", "domain": "algorithms", "difficulty": 0.4, "description": "Make locally optimal choice at each step"},
    {"name": "Divide and Conquer", "domain": "algorithms", "difficulty": 0.4, "description": "Split problem into independent subproblems, solve, merge"},
    {"name": "Backtracking", "domain": "algorithms", "difficulty": 0.5, "description": "Systematic trial-and-error: try, recurse, undo if failed"},
    # --- Operating Systems ---
    {"name": "Process", "domain": "os", "difficulty": 0.3, "description": "Instance of a running program with its own address space"},
    {"name": "Thread", "domain": "os", "difficulty": 0.35, "description": "Lightweight unit of execution sharing process address space"},
    {"name": "Mutex", "domain": "os", "difficulty": 0.45, "description": "Mutual exclusion lock for protecting shared resources"},
    {"name": "Semaphore", "domain": "os", "difficulty": 0.5, "description": "Counting synchronization primitive for resource limiting"},
    {"name": "Deadlock", "domain": "os", "difficulty": 0.5, "description": "Circular wait where no thread can proceed"},
    {"name": "Virtual Memory", "domain": "os", "difficulty": 0.5, "description": "Abstraction giving each process its own address space via paging"},
    {"name": "Page Replacement", "domain": "os", "difficulty": 0.55, "description": "Algorithm for choosing which page to evict (LRU, FIFO, Clock)"},
    # --- Networks ---
    {"name": "TCP", "domain": "networks", "difficulty": 0.4, "description": "Reliable, ordered, connection-oriented transport protocol"},
    {"name": "UDP", "domain": "networks", "difficulty": 0.35, "description": "Unreliable, connectionless transport protocol"},
    {"name": "DNS", "domain": "networks", "difficulty": 0.3, "description": "Domain Name System: maps hostnames to IP addresses"},
    {"name": "HTTP", "domain": "networks", "difficulty": 0.25, "description": "HyperText Transfer Protocol for web communication"},
    # --- Programming Languages ---
    {"name": "Pointer", "domain": "programming_languages", "difficulty": 0.4, "description": "Variable storing a memory address"},
    {"name": "Memory Allocation", "domain": "programming_languages", "difficulty": 0.45, "description": "Stack vs heap allocation, malloc/free, garbage collection"},
    {"name": "Polymorphism", "domain": "programming_languages", "difficulty": 0.4, "description": "Same interface, different implementations (compile/runtime)"},
    {"name": "Template", "domain": "programming_languages", "difficulty": 0.5, "description": "Generic programming: write code that works for multiple types"},
]

RELATIONS: list[dict] = [
    # Data structure prerequisites
    {"source": "Array", "target": "Linked List", "type": "contrasts_with"},
    {"source": "Array", "target": "Stack", "type": "prerequisite"},
    {"source": "Array", "target": "Queue", "type": "prerequisite"},
    {"source": "Array", "target": "Hash Table", "type": "prerequisite"},
    {"source": "Binary Tree", "target": "Binary Search Tree", "type": "prerequisite"},
    {"source": "Binary Search Tree", "target": "AVL Tree", "type": "prerequisite"},
    {"source": "Binary Search Tree", "target": "Red-Black Tree", "type": "prerequisite"},
    {"source": "Binary Search Tree", "target": "B-tree", "type": "builds_on"},
    {"source": "Binary Tree", "target": "Heap", "type": "builds_on"},
    {"source": "Hash Table", "target": "Graph", "type": "related"},
    {"source": "Linked List", "target": "Stack", "type": "builds_on"},
    {"source": "Linked List", "target": "Queue", "type": "builds_on"},
    {"source": "Linked List", "target": "Hash Table", "type": "related"},
    {"source": "String", "target": "Trie", "type": "prerequisite"},
    {"source": "Array", "target": "Union-Find", "type": "prerequisite"},
    # Algorithm prerequisites
    {"source": "Big-O Notation", "target": "Sorting", "type": "prerequisite"},
    {"source": "Recursion", "target": "DFS", "type": "prerequisite"},
    {"source": "Queue", "target": "BFS", "type": "prerequisite"},
    {"source": "Stack", "target": "DFS", "type": "prerequisite"},
    {"source": "Recursion", "target": "Dynamic Programming", "type": "prerequisite"},
    {"source": "Recursion", "target": "Backtracking", "type": "prerequisite"},
    {"source": "Divide and Conquer", "target": "Dynamic Programming", "type": "related"},
    {"source": "Sorting", "target": "Binary Search", "type": "prerequisite"},
    {"source": "Graph", "target": "BFS", "type": "prerequisite"},
    {"source": "Graph", "target": "DFS", "type": "prerequisite"},
    # OS prerequisites
    {"source": "Process", "target": "Thread", "type": "prerequisite"},
    {"source": "Thread", "target": "Mutex", "type": "prerequisite"},
    {"source": "Mutex", "target": "Semaphore", "type": "builds_on"},
    {"source": "Thread", "target": "Deadlock", "type": "prerequisite"},
    {"source": "Process", "target": "Virtual Memory", "type": "prerequisite"},
    {"source": "Virtual Memory", "target": "Page Replacement", "type": "prerequisite"},
    # Network relations
    {"source": "TCP", "target": "UDP", "type": "contrasts_with"},
    {"source": "DNS", "target": "HTTP", "type": "related"},
    # PL relations
    {"source": "Pointer", "target": "Memory Allocation", "type": "prerequisite"},
    {"source": "Template", "target": "Polymorphism", "type": "related"},
]


async def seed_database(db_url: str) -> dict:
    from studyagent.db.engine import create_session_factory
    from sqlalchemy.ext.asyncio import create_async_engine
    from studyagent.db.init import init_db
    from studyagent.db.repositories import ConceptRepo

    await init_db(db_url)
    engine = create_async_engine(db_url, connect_args={"check_same_thread": False})
    factory = create_session_factory(engine)

    concepts_created = 0
    relations_created = 0
    concept_map: dict[str, str] = {}

    async with factory() as session:
        repo = ConceptRepo(session)
        for c in CONCEPTS:
            concept = await repo.get_or_create(
                name=c["name"],
                domain=c["domain"],
                description=c.get("description"),
                difficulty=c.get("difficulty", 0.5),
                importance=0.5,
            )
            concept_map[c["name"]] = concept.id
            concepts_created += 1

        for r in RELATIONS:
            src_id = concept_map.get(r["source"])
            tgt_id = concept_map.get(r["target"])
            if src_id and tgt_id:
                try:
                    await repo.add_relation(
                        source_id=src_id, target_id=tgt_id,
                        relation_type=r["type"],
                    )
                    relations_created += 1
                except Exception:
                    pass

        await session.commit()

    await engine.dispose()
    return {"concepts": concepts_created, "relations": relations_created}


def main():
    import asyncio
    result = asyncio.run(seed_database("sqlite+aiosqlite:///./studyagent.db"))
    print(f"Seeded: {result['concepts']} concepts, {result['relations']} relations")


if __name__ == "__main__":
    main()
