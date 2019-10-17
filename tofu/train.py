from tofu import Tofu
from paintpose import PaintPoseDatset
import torchvision
from torchvision import datasets, transforms

if __name__ == "__main__":
    # Retrieve paintpose dataset if needed
    paintpose_path = "../datasets/wikiart"
    use_grayscale = False
    dataset = PaintPoseDatset(paintpose_path, use_grayscale, image_shape=(56, 56))

    # Train model
    model = Tofu(ls_dim=100, batch_size=32, input_shape=(56, 56))
    model.load_data(dataset)
    model.train_model()
