import matplotlib
from matplotlib import pyplot as plt

# make figure show in Pycharm
matplotlib.use('TkAgg')


def save(plt_pic, filename):
    plt_pic.savefig(filename)


def visualize_trajectory(trajectory, floor_plan_file, width, height, title=None, model=None,
                         show=False):
    # add trajectory
    size_list = [6] * trajectory.shape[0]
    size_list[0] = 10
    size_list[-1] = 10

    color_list = ['green'] * trajectory.shape[0]
    color_list[0] = 'red'
    color_list[-1] = 'blue'

    text_list = []
    for i in range(trajectory.shape[0]):
        text_list.append(f'Point: {i}')
    text_list[0] = 'Start Point: 0'
    text_list[-1] = f'End Point: {trajectory.shape[0] - 1}'

    # configure
    fig, ax = plt.subplots()
    fig.set_figheight(200 + 900 * height / width)
    fig.set_figwidth(900)
    font_dict = {'fontsize': 14,
                 'fontweight': 8.2,
                 'verticalalignment': 'baseline',
                 'horizontalalignment': 'left'}
    plt.title(title, fontdict=font_dict, loc='left')

    # add floor plan
    img = plt.imread(floor_plan_file)
    ax.imshow(img, extent=(0, width, 0, height))

    # hover event:show the trajectory

    sc = plt.scatter(
        x=trajectory[:, 0],
        y=trajectory[:, 1],
        s=size_list,
        color=color_list
    )

    if model.__contains__('lines'):
        plt.plot(trajectory[:, 0], trajectory[:, 1], color='black', lw=1, linestyle='dotted')

    if model.__contains__('markers'):

        position_count = {}
        for i in range(trajectory.shape[0]):
            if str(trajectory[i]) in position_count:
                position_count[str(trajectory[i])] += 1
            else:
                position_count[str(trajectory[i])] = 0
            plt.annotate(text_list[i], xy=(trajectory[:, 0][i], trajectory[:, 1][i]), xytext=(
                trajectory[:, 0][i] + 0.1, trajectory[:, 1][i] + 0.1 + 0.2 * (position_count[str(trajectory[i])])))

    if show:
        plt.show()


def visualize_heatmap(position, value, floor_plan_file, width, height, colorbar_title, title=None, show=False):
    # configure
    fig, ax = plt.subplots()
    fig.set_figheight(200 + 900 * height / width)
    fig.set_figwidth(900)
    font_dict = {'fontsize': 14,
                 'fontweight': 8.2,
                 'verticalalignment': 'baseline',
                 'horizontalalignment': 'left'}
    plt.title(title, fontdict=font_dict, loc='left')

    # add floor plan
    img = plt.imread(floor_plan_file)
    ax.imshow(img, extent=(0, width, 0, height))

    plt.scatter(
        x=position[:, 0],
        y=position[:, 1],
        c=value,
        cmap='gist_rainbow_r'
    )
    plt.colorbar(label=colorbar_title, orientation='horizontal')

    if show:
        plt.show()
