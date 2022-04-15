from utils.dataset import BBKDataset
import torch
from torch.utils.data import DataLoader
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.patches as mpatches
import numpy as np
from unet import UNet

# device
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

# dataset
bbkd = BBKDataset(zone = ("alles",),split="train", augment=False)
print(len(bbkd))
dl = DataLoader(bbkd, batch_size=16, shuffle=False)
x = next(iter(dl))

# load model
net = UNet(n_channels=7, n_classes=9, bilinear=False).to(device=device)
checkpoint_path = 'checkpoints_final_model/checkpoint_epoch27.pth'
net.load_state_dict(torch.load(checkpoint_path, map_location=device))

num = 1

# Labels and colors
# classes : "null","wooded_area", "water", "bushes", "individual_tree", "no_woodland", "ruderal_area", "without_vegetation", "buildings"
# rgb : [0,0,0], [0,104,0], [0, 192, 210], 
# hex : '#000000', '#006800','#00c0d2', '#73fe8c', '#00d200', '#fffac7', '#d7b384', '#d4d3d4', '#ed0038'
bbk_cmap = colors.ListedColormap(['#000000', '#006800','#00c0d2', '#73fe8c', '#00d200', '#fffac7', '#d7b384', '#d4d3d4', '#ed0038'])
bbk_scale = [0,1,2,3,4,5,6,7,8,9]
bbk_scale = [-0.5,0.5,1.5,2.5,3.5,4.5,5.5,6.5,7.5,8.5]
labels = ["null","wooded_area", "water", "bushes", "individual_tree", "no_woodland", "ruderal_area", "without_vegetation", "buildings"]
hex_colors = ['#000000', '#006800','#00c0d2', '#73fe8c', '#00d200', '#fffac7', '#d7b384', '#d4d3d4', '#ed0038']

# create a patch (proxy artist) for every color 
patches = [ mpatches.Patch(color=hex_colors[i], label=labels[i]) for i in range(len(hex_colors)) ]
# put those patched as legend-handles into the legend
#plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )

plt.figure()
#plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0. )
plt.legend(handles=patches, loc='center', ncol = 1, markerscale=2, fontsize='xx-large')
#fig.legend(handles=patches, loc=4, borderaxespad=0.)
plt.axis('off')
#plt.title('BBK legend')
plt.savefig(f'example_data/bbk_legend.png')

# counter = 0
# for i in dl:
# 	counter += 1
# 	document = i[0][num]
# 	rgbidsm = document[:5,:,:]*bbkd.std_vals_tiles+bbkd.mean_vals_tiles
# 	rgb = rgbidsm[:3,:,:].div(torch.max(rgbidsm[:3,:,:])).permute(1,2,0).numpy()
# 	#rgb = rgbidsm[:3,:,:].permute(1,2,0).numpy()
# 	# ir = rgbidsm[3,:,:].div(torch.max(rgbidsm[3,:,:])).numpy()
# 	ir = rgbidsm[3,:,:].numpy()
# 	# dsm = rgbidsm[4,:,:].div(torch.max(rgbidsm[4,:,:])).numpy()
# 	dsm = rgbidsm[4,:,:].numpy()
# 	build = document[5,:,:].numpy()
# 	hoe = document[6,:,:]*bbkd.std_vals_vegetation+bbkd.mean_vals_vegetation
# 	# hoe = hoe.div(torch.max(hoe)).numpy()
# 	hoe = hoe.numpy()
# 	bbk = i[1][num].argmax(dim=0).numpy()

# 	# print(np.shape(rgb))
# 	# print(np.shape(ir))
# 	# print(np.shape(dsm))
# 	# print(np.shape(build))
# 	# print(np.shape(hoe))
# 	# print(np.shape(bbk))

# 	fig = plt.figure()
# 	plt.subplot(231)
# 	plt.imshow(rgb)
# 	# plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=0.4)
# 	plt.axis('off')
# 	plt.title('RGB')
# 	plt.subplot(232)
# 	plt.imshow(ir, cmap='Reds', norm=colors.Normalize())
# 	plt.axis('off')
# 	plt.title('IR')
# 	plt.subplot(233)
# 	plt.imshow(dsm, norm=colors.Normalize())
# 	plt.axis('off')
# 	plt.title('DSM')
# 	plt.subplot(234)
# 	plt.imshow(build, cmap='Greys')
# 	plt.axis('off')
# 	plt.title('Build')
# 	plt.subplot(235)
# 	plt.imshow(hoe, cmap='Greens', norm=colors.Normalize())
# 	plt.axis('off')
# 	plt.title('HOE')
# 	plt.subplot(236)
# 	plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1))
# 	plt.axis('off')
# 	plt.title('BBK')
# 	plt.tight_layout()
# 	plt.savefig(f'example_data/example_data{counter}.png')

counter = 0
for i in dl:
	for j in range(len(i[0])):
		bbk = i[1][j].argmax(dim=0)
		if torch.unique(bbk[bbk!=0], return_counts=False).size(0) == 8:
			doc = i[0].clone().detach().to(device=device)
			print(doc.size())
			prediction = net(doc)[j]
			prediction = torch.softmax(prediction, dim=0).argmax(dim=0).cpu().numpy()
			print(np.shape(prediction))
			print(np.unique(prediction))
			print(torch.unique(bbk[bbk!=0], return_counts=False).size())
			bbk = bbk.numpy()
			counter += 1
			document = i[0][j]
			rgbidsm = document[:5,:,:]*bbkd.std_vals_tiles+bbkd.mean_vals_tiles
			rgb = rgbidsm[:3,:,:].div(torch.max(rgbidsm[:3,:,:])).permute(1,2,0).numpy()
			ir = rgbidsm[3,:,:].numpy()
			dsm = rgbidsm[4,:,:].numpy()
			build = document[5,:,:].numpy()
			hoe = document[6,:,:]*bbkd.std_vals_vegetation+bbkd.mean_vals_vegetation
			hoe = hoe.numpy()

			# prediction image
			fig = plt.figure()
			plt.subplot(131)
			plt.imshow(rgb)
			# plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=0.4)
			plt.axis('off')
			plt.title('RGB')
			plt.subplot(132)
			#plt.imshow(rgb)
			plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=1)
			plt.axis('off')
			plt.title('BBK')
			plt.subplot(133)
			#plt.imshow(rgb)
			plt.imshow(prediction, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=1)
			plt.axis('off')
			plt.title('Prediction')
			plt.tight_layout()
			plt.savefig(f'example_data/example_pred{counter}.png')
			plt.close()

			# data image
			fig = plt.figure()
			plt.subplot(231)
			plt.imshow(rgb)
			# plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=0.4)
			plt.axis('off')
			plt.title('RGB')
			plt.subplot(232)
			plt.imshow(ir, cmap='Reds', norm=colors.Normalize())
			plt.axis('off')
			plt.title('IR')
			plt.subplot(233)
			plt.imshow(dsm, norm=colors.Normalize())
			plt.axis('off')
			plt.title('DSM')
			plt.subplot(234)
			plt.imshow(build, cmap='Greys')
			plt.axis('off')
			plt.title('Build')
			plt.subplot(235)
			plt.imshow(hoe, cmap='Greens', norm=colors.Normalize())
			plt.axis('off')
			plt.title('HOE')
			plt.subplot(236)
			plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1))
			plt.axis('off')
			plt.title('BBK')
			plt.tight_layout()
			plt.savefig(f'example_data/example_data{counter}.png')
			plt.close()
			if counter == 15:
				break
print(f'number of resulting images : {counter}')
			

""" pred = net(x[0].to(device=device))
counter = 0
for j in range(len(x[0])):
	bbk = x[1][j].argmax(dim=0)
	doc = x[0][j].clone().detach().to(device=device).unsqueeze(dim=0)
	print(doc.size())
	prediction = pred[j]
	prediction = prediction.argmax(dim=0).cpu().numpy()
	print(np.shape(prediction))
	print(np.unique(prediction))
	bbk = bbk.numpy()
	counter += 1
	document = x[0][j]
	rgbidsm = document[:5,:,:]*bbkd.std_vals_tiles+bbkd.mean_vals_tiles
	rgb = rgbidsm[:3,:,:].div(torch.max(rgbidsm[:3,:,:])).permute(1,2,0).numpy()
	ir = rgbidsm[3,:,:].numpy()
	dsm = rgbidsm[4,:,:].numpy()
	build = document[5,:,:].numpy()
	hoe = document[6,:,:]*bbkd.std_vals_vegetation+bbkd.mean_vals_vegetation
	hoe = hoe.numpy()

	# prediction image
	fig = plt.figure()
	plt.subplot(131)
	plt.imshow(rgb)
	# plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=0.4)
	plt.axis('off')
	plt.title('RGB')
	plt.subplot(132)
	#plt.imshow(rgb)
	plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=1)
	plt.axis('off')
	plt.title('BBK')
	plt.subplot(133)
	#plt.imshow(rgb)
	plt.imshow(prediction, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=1)
	plt.axis('off')
	plt.title('prediction')
	plt.tight_layout()
	plt.savefig(f'example_data/example_pred{counter}.png')
	plt.close()

	# data image
	fig = plt.figure()
	plt.subplot(231)
	plt.imshow(rgb)
	# plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1), alpha=0.4)
	plt.axis('off')
	plt.title('RGB')
	plt.subplot(232)
	plt.imshow(ir, cmap='Reds', norm=colors.Normalize())
	plt.axis('off')
	plt.title('IR')
	plt.subplot(233)
	plt.imshow(dsm, norm=colors.Normalize())
	plt.axis('off')
	plt.title('DSM')
	plt.subplot(234)
	plt.imshow(build, cmap='Greys')
	plt.axis('off')
	plt.title('Build')
	plt.subplot(235)
	plt.imshow(hoe, cmap='Greens', norm=colors.Normalize())
	plt.axis('off')
	plt.title('HOE')
	plt.subplot(236)
	plt.imshow(bbk, cmap=bbk_cmap, norm=colors.BoundaryNorm(bbk_scale, len(bbk_scale)-1))
	plt.axis('off')
	plt.title('BBK')
	plt.tight_layout()
	plt.savefig(f'example_data/example_data{counter}.png')
	plt.close()
	if counter == 15:
		break
print(f'number of resulting images : {counter}') """



















