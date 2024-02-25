"""Contains classes for generating data structures."""

from generation.structures.tree import BinaryTree, BinarySearchTree
from generation.structures.graph import UndirectedGraph, DirectedGraph
from utils.serializer import add_object
from utils.colors import Colors
from utils.logger import Logger
from utils.files import validate_path, check_path_exists, has_negative_value
import os

from pathlib import Path
import yaml
from time import perf_counter
from typing import Type, Optional, TypeVar, Literal
import itertools
from uuid import uuid4, UUID

logger = Logger(__name__)

Color = Literal['#abe0f9', '#fee4b3', '#eeeeee']
Shape = Literal['o', 's', 'd']
Font = Literal['sans-serif', 'serif', 'monospace']
Width = Literal['0.5', '1.0', '1.5']

colors = ['#abe0f9', '#fee4b3', '#eeeeee']
shapes = ['o', 's', 'd']
fonts = ['sans-serif', 'serif', 'monospace']
widths = ['0.5', '1.0', '1.5']

Structure = TypeVar('Structure', BinaryTree, BinarySearchTree, UndirectedGraph, DirectedGraph)

StructureAbbreviation = Literal['bit', 'bst', 'udg', 'dig']
YamlName = Literal['binary_tree.yaml', 'binary_search_tree.yaml', 'undirected_graph.yaml', 'directed_graph.yaml']

class Generator:
    """
    Generator class for generating data structures.

    Example
    -------
    ```python
    from generation.generator import Generator
    generator = Generator()
    ```
    """

    def generate_structure(self, structure_class: Type[Structure], large: bool = False) -> Type[Structure]:
        """
        Generates an empty structure instance and returns it.
        
        Parameters
        ----------
        structure_class : Type[Structure]
            the structure to generate
        large : bool (default: False)
            whether or not the structure should be large (11-20 nodes)
            
        Returns
        -------
        Type[Structure]
            the generated structure instance
        """

        print(Colors.OKBLUE + "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" + Colors.ENDC)

        logger.info(f"Generating {structure_class.formal_name}...")
        start = perf_counter()
        
        structure_instance = structure_class(large=large)
        structure_instance.generate()
        
        end = perf_counter()
        logger.info(f"╰── Generated {structure_class.formal_name} in {round(end - start, 2)} seconds.")
        
        return structure_instance

    def fill_structure(self, structure_instance: Type[Structure]) -> Type[Structure]:
        """
        Fills the structure instance and returns it.
        
        Parameters
        ----------
        structure_instance : Type[Structure]
            the structure instance to fill
            
        Returns
        -------
        Type[Structure]
            the filled structure instance
        """
        print(Colors.OKBLUE + "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄" + Colors.ENDC)
        
        logger.info(f"Filling {structure_instance.formal_name}...")
        start = perf_counter()
        
        structure_instance.fill() # fill structure
        
        end = perf_counter()
        logger.info(f"╰── Filled {structure_instance.formal_name} in {round(end - start, 2)} seconds.")
        
        return structure_instance

    def draw_structure(self, structure_instance: Type[Structure], uuid: UUID = None, text: str = None, expected: str = None, yaml: bool = False, yaml_path: Path = Path('.'), yaml_name: Optional[str] = None, save: bool = False, save_path: Path = Path('.'), save_name: Optional[str] = None, show: bool = True, run: int = 0, generation: int = 0, variation: int = 0, format: int = 0, shape: Shape = 'o', color: Color = '#fee4b3', font: Font = 'sans-serif', width: Width = '1.0') -> None:
        """
        Draws the structure instance and saves the image to a file and/or adds the object to a YAML file.
        
        Parameters
        ----------
        structure_instance : Type[Structure]
            the structure instance to fill
        uuid : UUID (default: None)
            the UUID of the object
        text : str (default: None)
            the text to add to the YAML file
        expected : str (default: None)
            the expected output of the model
        yaml : bool (default: False)
            whether or not to add the object to a YAML file
        yaml_path : Path (default: Path('.'))
            the path to the YAML file
        yaml_name : Optional[str] (default: None)
            the name of the YAML file
        save : bool (default: False)
            whether or not to save the image
        save_path : Path (default: Path('.'))
            the path to the image
        save_name : Optional[str] (default: None)
            the name of the image file
        show : bool (default: True)
            whether or not to show the image
        run : int (default: 0)
            the run number
        generation : int (default: 0)
            the generation number
        variation : int (default: 0)
            the variation number
        format : int (default: 0)
            the format number
        shape : Shape (default: 'o')
            the shape of the nodes
        color : Color (default: '#abe0f9')
            the color of the nodes
        font : Font (default: 'sans-serif')
            the font of the text
        width : Width (default: '1.0')
            the width of the edges
        
        Raises
        ------
        ValueError
            if generation, variation, or format is negative
        """
        print(Colors.OKBLUE + "┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄" + Colors.ENDC)

        if not save:
            if not show:
                logger.error("Neither save nor show is True, so the image will not be generated.")
                return
            if save_path != Path('.') or save_name:
                logger.warning("The save_path and save_name parameters are ignored since save is False.")
            if yaml:
                logger.warning("The yaml parameter is ignored since save is False.")

        if not yaml:
            if yaml_path != Path('.') or yaml_name:
                logger.warning("The yaml_path and yaml_name parameters are ignored since yaml is False.")
        if not yaml_name:
            yaml_name = structure_instance.yaml_structure_type + '.yaml'
        if not save_name:
            save_name = structure_instance.default_file_name
            
        filepath = validate_path(save_path, save_name, '.png')
        datapath = validate_path(yaml_path, yaml_name, '.yaml')

        if has_negative_value([run, generation, variation, format]):
            raise ValueError("Generation, variation, and format must be non-negative integers.")
        
        logger.info(f"Drawing {structure_instance.formal_name}...")
        start = perf_counter()
        
        structure_instance.draw(save=save, path=filepath, show=show, shape=shape, color=color, font=font, width=width)
        
        end = perf_counter()
        logger.info(f"╰── Drew {structure_instance.formal_name} in {round(end - start, 2)} seconds.")
        
        if save:
            logger.info(f"{structure_instance.formal_name} image saved to {filepath}.")
            if yaml:
                try:
                    add_object(
                        uuid=uuid,
                        file_path=datapath,
                        text=text,
                        image_path=filepath,
                        expected=expected,
                        structure=structure_instance.yaml_structure_type,
                        run=run,
                        generation=generation,
                        variation=variation,
                        format=format,
                        color=color,
                        font=font,
                        width=width,
                    )
                    logger.info(f"{structure_instance.formal_name} added to YAML file at {datapath}.")
                except Exception as e:
                    logger.error(f"Failed to add binary tree to YAML: {e}")
                    
class BatchGenerator(Generator):
    """
    Generate data structures in batches.
    
    Example
    -------
    ```python
    from generation.generator import BatchGenerator
    batch_generator = BatchGenerator()
    ```
    """
    generator: Generator
    
    def __init__(self) -> None:
        """
        Initializes the BatchGenerator class.
        """
        self.generator = Generator()

    def generate_batch(self, structure_class: Type[Structure], type: StructureAbbreviation, yaml_name: YamlName, yaml_path: Path, save_path: Path, text_path: Path, text_name: Path, generations: int = 1, variations: int = 1, visual_combinations: bool = False) -> None:
        """
        Generates a batch of data structures.
        
        Parameters
        ----------
        structure_class : Type[Structure]
            the structure to generate
        type : StructureAbbreviation
            the abbreviation of the structure
        yaml_name : YamlName
            the name of the YAML file
        yaml_path : Path
            the path to the YAML file
        save_path : Path
            the path to save the images
        text_path : Path
            the path to the text file
        text_name : Path
            the name of the text file
            
        Example
        -------
        ```python
        batch_generator = BatchGenerator()
        batch_generator.generate_batch(
            structure_class=BinaryTree,
            type='bit',
            yaml_name='binary_tree.yaml',
            yaml_path=yaml_path,
            save_path=image_path_binary_tree,
            text_path=text_path,
            text_name='binary_tree_text.yaml',
        )
        ```
        
        Notes
        -----
        The YAML file has a default format for evaluation. This format is generated by the `BatchGenerator` and is as follows:
        
        ```yaml
        - color: '#88d7fe'
          expected: '[30, 71, 56, 69, 42, 19, 25]'
          font: serif
          format: 2
          generation: 1
          id: eab69c75-2644-496b-806e-fb6daa36347a
          image_path: images/binary_tree/bit_run-2_gen-1_var-1_fmt-2_thk-05_clr-88d7fe_fnt-serif_idn-eab69c75-2644-496b-806e-fb6daa36347a.png
          structure: binary_tree
          text: Provide a single-line python list representing the post-order traversal of
            the binary tree.
          width: '0.5'
          variation: 1
        ```
        """
        run = 1
        format = 1
        
        for file_path in save_path.iterdir():
            if file_path.is_file() or file_path.is_symlink():
                file_path.unlink()
        
        text_path_joined = validate_path(text_path, text_name, '.yaml')
        yaml_path_joined = validate_path(yaml_path, yaml_name, '.yaml')
        
        with open(yaml_path_joined, 'w') as file:
            file.write('')
        with open(text_path_joined, 'r') as file:
            text_prompts = yaml.safe_load(file)
        
        # create base structures
        for generation in range(1, generations + 1):
            
            approved = False
            structure_generated = None
            
            while not approved:
                
                test_path = check_path_exists(Path('images/'))
                test_name = 'test.png'
                
                structure_generated = self.generator.generate_structure(structure_class=structure_class, large=False)
                structure_filled = self.generator.fill_structure(structure_instance=structure_generated)
                self.generator.draw_structure(
                    structure_instance=structure_filled,
                    yaml=False,
                    save=True,
                    save_path=test_path,
                    save_name=test_name,
                    show=False,
                )
                
                logger.warning(f"Check {test_path / test_name}. Approve this generation?\n\n(Y) Approved, continue generating\n(N) Denied, regenerate\n(X) Exit\n")
                input_approved = input(">>> ")
                
                if input_approved.lower() == 'y':
                    approved = True
                elif input_approved.lower() == 'x':
                    return
            
            # create variations of each base structure
            for variation in range(1, variations + 1):
                
                structure_filled = self.generator.fill_structure(structure_instance=structure_generated)
                        
                if visual_combinations:
                    
                    format_combinations = list(itertools.product(width, colors, fonts))

                    for width, color, font in format_combinations:
                        
                        uuid = uuid4()
                        
                        for text in text_prompts:
                            
                            expected = None
                            method_name = text['type']
                            if hasattr(structure_filled, method_name):
                                method_to_call = getattr(structure_filled, method_name)
                                expected = method_to_call(structure_filled)
                            else:
                                logger.error(f"Method '{method_name}' not found in {structure_filled}.")
                            
                            self.generator.draw_structure(
                                uuid=uuid,
                                structure_instance=structure_filled,
                                text=text['text'],
                                expected=str(expected),
                                yaml=True,
                                yaml_path=yaml_path,
                                yaml_name=yaml_name,
                                save=True,
                                save_path=save_path,
                                save_name=f"{type}_run-{run}_gen-{generation}_var-{variation}_fmt-{format}_thk-{width.replace('.', '')}_clr-{color.replace('#', '')}_fnt-{font.replace('-', '')}_idn-{str(uuid)}.png",
                                show=False,
                                run=run,
                                generation=generation,
                                variation=variation,
                                format=format,
                                color=color,
                                font=font,
                                width=width,
                            )
                            
                        format += 1
                        run += 1
                        
                else:
                    
                    uuid = uuid4()
                    
                    for text in text_prompts:
                        
                        expected = None
                        method_name = text['type']
                        if hasattr(structure_filled, method_name):
                            method_to_call = getattr(structure_filled, method_name)
                            expected = method_to_call(structure_filled)
                        else:
                            logger.error(f"Method '{method_name}' not found in {structure_filled}.")
                            
                        self.generator.draw_structure(
                            uuid=uuid,
                            structure_instance=structure_filled,
                            text=text['text'],
                            expected=str(expected),
                            yaml=True,
                            yaml_path=yaml_path,
                            yaml_name=yaml_name,
                            save=True,
                            save_path=save_path,
                            save_name=f"{type}_run-{run}_gen-{generation}_var-{variation}_fmt-{format}_thk-10_clr-88d7fe_fnt-sansserif_idn-{str(uuid)}.png",
                            show=False,
                            run=run,
                            generation=generation,
                            variation=variation,
                            format=format,
                        )
                            
                    run += 1