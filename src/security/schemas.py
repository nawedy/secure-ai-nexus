class TreeNode:
    """
    Represents a node in a binary tree.

    Attributes:
        val (int): The value stored in the node.
        left (TreeNode): The left child of the node.
        right (TreeNode): The right child of the node.
    """

    def __init__(self, val=0, left=None, right=None):
        """
        Initializes a TreeNode object.

        Args:
            val (int, optional): The value of the node. Defaults to 0.
            left (TreeNode, optional): The left child node. Defaults to None.
            right (TreeNode, optional): The right child node. Defaults to None.
        """
        self.val = val
        self.left = left
        self.right = right


def is_same_tree(p: TreeNode, q: TreeNode) -> bool:
    """
    Checks if two binary trees are the same.

    Args:
        p (TreeNode): The root of the first binary tree.
        q (TreeNode): The root of the second binary tree.

    Returns:
        bool: True if the trees are the same, False otherwise.
    """
    if not p and not q:
        return True
    if not p or not q:
        return False
    if p.val != q.val:
        return False
    return is_same_tree(p.left, q.left) and is_same_tree(p.right, q.right)


def invert_tree(root: TreeNode) -> TreeNode:
    """
    Inverts a binary tree.

    Args:
        root (TreeNode): The root of the binary tree to invert.

    Returns:
        TreeNode: The root of the inverted binary tree.
    """
    if not root:
        return None
    root.left, root.right = root.right, root.left
    invert_tree(root.left)
    invert_tree(root.right)
    return root


def max_depth(root: TreeNode) -> int:
    """
    Calculates the maximum depth of a binary tree.

    Args:
        root (TreeNode): The root of the binary tree.

    Returns:
        int: The maximum depth of the binary tree.
    """
    if not root:
        return 0
    left_depth = max_depth(root.left)
    right_depth = max_depth(root.right)
    return max(left_depth, right_depth) + 1