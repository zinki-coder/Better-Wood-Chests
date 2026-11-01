package betterwoodchests.modid.client;

import betterwoodchests.modid.BetterWoodChests;
import betterwoodchests.modid.WoodChestBlockEntity;
import com.mojang.blaze3d.vertex.PoseStack;
import it.unimi.dsi.fastutil.floats.Float2FloatFunction;
import it.unimi.dsi.fastutil.ints.Int2IntFunction;
import java.util.HashMap;
import java.util.Map;
import net.minecraft.client.model.object.chest.ChestModel;
import net.minecraft.client.renderer.MultiblockChestResources;
import net.minecraft.client.renderer.Sheets;
import net.minecraft.client.renderer.SubmitNodeCollector;
import net.minecraft.client.renderer.blockentity.BlockEntityRenderer;
import net.minecraft.client.renderer.blockentity.BlockEntityRendererProvider;
import net.minecraft.client.renderer.blockentity.BrightnessCombiner;
import net.minecraft.client.renderer.blockentity.ChestRenderer;
import net.minecraft.client.renderer.feature.ModelFeatureRenderer;
import net.minecraft.client.renderer.state.level.CameraRenderState;
import net.minecraft.client.renderer.texture.OverlayTexture;
import net.minecraft.client.resources.model.sprite.SpriteGetter;
import net.minecraft.client.resources.model.sprite.SpriteId;
import net.minecraft.core.registries.BuiltInRegistries;
import net.minecraft.resources.Identifier;
import net.minecraft.world.level.block.ChestBlock;
import net.minecraft.world.level.block.DoubleBlockCombiner.Combiner;
import net.minecraft.world.level.block.DoubleBlockCombiner.NeighborCombineResult;
import net.minecraft.world.level.block.entity.ChestBlockEntity;
import net.minecraft.world.level.block.state.BlockState;
import net.minecraft.world.level.block.state.properties.ChestType;
import net.minecraft.world.phys.Vec3;

public class WoodChestRenderer implements BlockEntityRenderer<WoodChestBlockEntity, WoodChestRenderState> {
    private final SpriteGetter sprites;
    private final MultiblockChestResources<ChestModel> models;
    private final Map<String, MultiblockChestResources<SpriteId>> textures = new HashMap<>();

    public WoodChestRenderer(final BlockEntityRendererProvider.Context context) {
        this.sprites = context.sprites();
        this.models = ChestRenderer.LAYERS.map(layer -> new ChestModel(context.bakeLayer(layer)));
    }

    private MultiblockChestResources<SpriteId> textures(final String wood) {
        return this.textures.computeIfAbsent(wood, w -> new MultiblockChestResources<>(
            sprite(w), sprite(w + "_left"), sprite(w + "_right")));
    }

    private static SpriteId sprite(final String name) {
        return Sheets.CHEST_MAPPER.apply(Identifier.fromNamespaceAndPath(BetterWoodChests.MOD_ID, name));
    }

    @Override
    public WoodChestRenderState createRenderState() {
        return new WoodChestRenderState();
    }

    @Override
    public void extractRenderState(
        final WoodChestBlockEntity blockEntity,
        final WoodChestRenderState state,
        final float partialTicks,
        final Vec3 cameraPosition,
        final ModelFeatureRenderer.CrumblingOverlay breakProgress
    ) {
        BlockEntityRenderer.super.extractRenderState(blockEntity, state, partialTicks, cameraPosition, breakProgress);
        boolean hasLevel = blockEntity.getLevel() != null;
        BlockState blockState = blockEntity.getBlockState();
        state.type = blockState.hasProperty(ChestBlock.TYPE) ? blockState.getValue(ChestBlock.TYPE) : ChestType.SINGLE;
        state.facing = blockState.getValue(ChestBlock.FACING);
        String path = BuiltInRegistries.BLOCK.getKey(blockState.getBlock()).getPath();
        state.wood = path.endsWith("_chest") ? path.substring(0, path.length() - "_chest".length()) : "oak";
        NeighborCombineResult<? extends ChestBlockEntity> combineResult;
        if (hasLevel && blockState.getBlock() instanceof ChestBlock chestBlock) {
            combineResult = chestBlock.combine(blockState, blockEntity.getLevel(), blockEntity.getBlockPos(), true);
        } else {
            combineResult = Combiner::acceptNone;
        }
        state.open = ((Float2FloatFunction) combineResult.apply(ChestBlock.opennessCombiner(blockEntity))).get(partialTicks);
        if (state.type != ChestType.SINGLE) {
            state.lightCoords = ((Int2IntFunction) combineResult.apply(new BrightnessCombiner())).applyAsInt(state.lightCoords);
        }
    }

    @Override
    public void submit(
        final WoodChestRenderState state,
        final PoseStack poseStack,
        final SubmitNodeCollector submitNodeCollector,
        final CameraRenderState camera
    ) {
        poseStack.pushPose();
        poseStack.mulPose(ChestRenderer.modelTransformation(state.facing));
        float open = state.open;
        open = 1.0F - open;
        open = 1.0F - open * open * open;
        SpriteId spriteId = textures(state.wood).select(state.type);
        ChestModel model = this.models.select(state.type);
        submitNodeCollector.submitModel(model, open, poseStack, state.lightCoords,
            OverlayTexture.NO_OVERLAY, -1, spriteId, this.sprites, 0, state.breakProgress);
        poseStack.popPose();
    }
}
