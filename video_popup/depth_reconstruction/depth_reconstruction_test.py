import os
import numpy as np
import cPickle as pickle

import logging

from video_popup.utils import util
from depth_reconstruction import DepthReconstruction

expr = 'kitti_sequence'
#expr = 'kitti_rigid'
#expr = 'kitti_dense'

_PACKAGE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_ROOT_PATH = os.path.dirname(_PACKAGE_PATH)

if(expr == 'kitti_sequence'):
    for image_index in range(15):

	    print image_index

	    seg_file = os.path.join(
		_ROOT_PATH,
		'data/Kitti/05/broxmalik_Size4/broxmalikResults/f1t15/v5/' \
		'vw10_nn10_k5_thresh10000_max_occ12_op0_cw2.5/init200/mdl2000_pw10000_oc10_engine0_it5/results.pkl'
	    )

	    bin_gt_file = os.path.join(
		_ROOT_PATH,
		'data/Kitti/05/broxmalik_Size4/002491.bin'
	    )

	    K = np.array([[707.0912, 0,  601.8873],
			  [0,  707.0912, 183.1104],
			  [0,        0,       1]])

	    with open(seg_file, 'r') as f:
		seg = pickle.load(f)

	    Z = seg['Z']
	    mask = np.logical_and(Z[0], Z[1])

	    W = seg['W'][2*image_index:2*image_index+2,mask]
	    Z = seg['Z'][image_index:image_index+2,mask]
	    labels = seg['labels_objects'][mask]
	    images = seg['images'][image_index:image_index+2]


	    # plot the segmentation result
	    #util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_objects'])
	    #util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_parts'])

	    data = (W, Z, labels, K, images)
	    print images

	    # parameters
	    # num_segments
	    # lambda_reg, kappa, gamma

	    para = {}
	    para['seg_folder'] = os.path.dirname(seg_file)
	    para['num_segments'] = 5000
	    para['lambda_reg_list'] = [100]
	    para['kappa_list'] = [1]
	    para['gamma_list'] = [1]

	    para['has_gt'] = 0
	    para['expr'] = 'kitti'

	    Tr = np.array([[-0.001857739385241,  -0.999965951351000,  -0.008039975204516,  -0.004784029760483],
			   [-0.006481465826011,   0.008051860151134,  -0.999946608177400,  -0.073374294642310],
			   [0.999977309828700,  -0.001805528627661,  -0.006496203536139,  -0.333996806443300]])

	    para['Tr'] = Tr
	    para['bin_gt_file'] = bin_gt_file

	    logging.basicConfig(filename=para['seg_folder'] + '/record.log', level=logging.DEBUG,
				format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

	    depth_map_recons = DepthReconstruction(data, para)

	    depth_map_recons.run()

            point_cloud_parent = os.path.join(os.path.dirname(seg_file), 'SuperPixels')
            for file_name in ['points_dense', 'points_sparse', 'points_dense_linear']:
                os.rename(os.path.join(point_cloud_parent, file_name + '.mat'), os.path.join(point_cloud_parent, file_name + '_' + str(image_index) + '.mat'))

elif(expr == 'kitti_rigid'):

    print expr

    seg_file = os.path.join(
        _ROOT_PATH,
       'data/Kitti/05_rigid2/broxmalik_Size2/broxmalikResults/f1t2/v1/' \
       'vw10_nn10_k1_thresh100_max_occ2_op0_cw2.5/init200/mdl20000_pw3000_oc10_engine0_it5/results.pkl'
    )

    bin_gt_file = os.path.join(
        _ROOT_PATH,
        'data/Kitti/05_rigid2/broxmalik_Size2/002648.bin'
    )

    K = np.array([[707.0912, 0,  601.8873],
                  [0,  707.0912, 183.1104],
                  [0,        0,       1]])

    with open(seg_file, 'r') as f:
        seg = pickle.load(f)

    Z = seg['Z']
    mask = np.logical_and(Z[0], Z[1])

    W = seg['W'][0:4,mask]
    Z = seg['Z'][0:2,mask]
    labels = seg['labels'][mask]
    images = seg['images'][0:2]


    # plot the segmentation result
    #util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_objects'])
    #util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_parts'])

    data = (W, Z, labels, K, images)
    print images

    # parameters
    # num_segments
    # lambda_reg, kappa, gamma

    para = {}
    para['seg_folder'] = os.path.dirname(seg_file)
    para['num_segments'] = 5000
    para['lambda_reg_list'] = [100]
    para['kappa_list'] = [1]
    para['gamma_list'] = [1]

    para['has_gt'] = 0
    para['expr'] = 'kitti'

    Tr = np.array([[-0.001857739385241,  -0.999965951351000,  -0.008039975204516,  -0.004784029760483],
                   [-0.006481465826011,   0.008051860151134,  -0.999946608177400,  -0.073374294642310],
                   [0.999977309828700,  -0.001805528627661,  -0.006496203536139,  -0.333996806443300]])

    para['Tr'] = Tr
    para['bin_gt_file'] = bin_gt_file

    logging.basicConfig(filename=para['seg_folder'] + '/record.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    depth_map_recons = DepthReconstruction(data, para)

    depth_map_recons.run()

elif(expr == 'kitti_dense'):

    seg_file = os.path.join(
        _ROOT_PATH,
        'data/Kitti/05_2f/dense_flow/epicflowResults/f1t2/v1_d4/' \
        'vw10_nn10_k1_thresh100_max_occ2_op0_cw2.5/init200/mdl1000_pw10000_oc10_engine0_it5/results.pkl'
    )

    K = np.array([[707.0912, 0,  601.8873],
                  [0,  707.0912, 183.1104],
                  [0,        0,       1]])

    with open(seg_file, 'r') as f:
        seg = pickle.load(f)

    Z = seg['Z']
    mask = np.logical_and(Z[0], Z[1])

    W = seg['W'][0:4,mask]
    Z = seg['Z'][0:2,mask]
    labels = seg['labels'][mask]
    images = seg['images'][0:2]

    # plot the segmentation result
    # util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_objects'])
    # util.plot_nbor(seg['W'], seg['Z'], seg['s'], seg['images'], seg['labels_parts'])

    data = (W, Z, labels, K, images)

    # parameters
    # num_segments
    # lambda_reg, kappa, gamma

    para = {}
    para['seg_folder'] = os.path.dirname(seg_file)
    para['num_segments'] = 5000
    para['lambda_reg_list'] = [0]
    para['kappa_list'] = [1]
    para['gamma_list'] = [1]
    para['lambda_reg2_list'] = [5]
    para['lambda_constr_list'] = [10000]

    para['has_gt'] = 1
    para['expr'] = 'kitti'

    Tr = np.array([[-0.001857739385241,  -0.999965951351000,  -0.008039975204516,  -0.004784029760483],
                   [-0.006481465826011,   0.008051860151134,  -0.999946608177400,  -0.073374294642310],
                   [0.999977309828700,  -0.001805528627661,  -0.006496203536139,  -0.333996806443300]])

    para['Tr'] = Tr
    para['bin_gt_file'] = os.path.join(_ROOT_PATH, 'data/Kitti/05_2f/002491.bin')

    logging.basicConfig(filename=para['seg_folder'] + '/record.log', level=logging.DEBUG,
                        format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

    depth_map_recons = DepthReconstruction(data, para)

    depth_map_recons.run()

