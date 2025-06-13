from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter


text= """
The History and Impact of Quantum Mechanics

Quantum mechanics is a fundamental theory in physics that describes nature at the smallest scales, such as atoms and subatomic particles. It was developed in the early 20th century, revolutionizing our understanding of the physical world.

The origins of quantum mechanics trace back to Max Planck’s work in 1900, where he introduced the idea of quantized energy levels to explain blackbody radiation. This concept was further developed by Albert Einstein in 1905 when he explained the photoelectric effect by proposing that light consists of discrete packets of energy called photons. Einstein’s work earned him the Nobel Prize in Physics in 1921.

Building on these ideas, Niels Bohr proposed the Bohr model of the atom in 1913, which described electrons orbiting the nucleus in fixed energy levels. This model successfully explained the spectral lines of hydrogen but had limitations with more complex atoms.

In the 1920s, Werner Heisenberg formulated matrix mechanics, and Erwin Schrödinger developed wave mechanics, two equivalent formulations of quantum mechanics. Schrödinger’s wave equation describes how the quantum state of a physical system changes over time.

Werner Heisenberg is also famous for the uncertainty principle, which states that certain pairs of physical properties, like position and momentum, cannot be simultaneously known to arbitrary precision.

Quantum mechanics has had profound implications beyond physics. It laid the foundation for quantum chemistry, explaining chemical bonding and reactions. It also enabled the development of semiconductors, which are the basis for modern electronics, including computers and smartphones.

Richard Feynman, a prominent physicist of the 20th century, contributed significantly to quantum electrodynamics (QED), a quantum theory of the interaction between light and matter. Feynman introduced Feynman diagrams, a pictorial representation of particle interactions.

The theory of quantum mechanics also paved the way for emerging fields such as quantum computing and quantum cryptography. Quantum computers use quantum bits, or qubits, which can represent both 0 and 1 simultaneously, promising exponential speedups for certain computational problems.

Despite its successes, quantum mechanics challenges our classical intuitions about reality. Concepts like superposition and entanglement defy everyday experience but have been experimentally confirmed.

The Copenhagen interpretation, primarily developed by Niels Bohr and Werner Heisenberg, is one of the earliest and most widely taught interpretations of quantum mechanics. It emphasizes the probabilistic nature of quantum measurements and the role of the observer.

Today, research in quantum mechanics continues to expand, with scientists exploring quantum gravity, quantum field theory, and applications in materials science and information technology.

"""


def get_nodes(text=text):
    """Convert text to nodes for processing."""
    # Assuming the text is already cleaned and ready for processing
    documents = [Document(text=text)]

    splitter = SentenceSplitter(
        chunk_size=1024,
        chunk_overlap=20,
    )
    nodes = splitter.get_nodes_from_documents(documents)

    return nodes